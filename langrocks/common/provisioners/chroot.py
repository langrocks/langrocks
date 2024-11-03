import logging
import os
from typing import Any, List

from jupyter_client import KernelConnectionInfo, launch_kernel
from jupyter_client.provisioning import LocalProvisioner

logger = logging.getLogger(__name__)


class ChrootProvisioner(LocalProvisioner):

    async def launch_kernel(self, cmd: List[str], **kwargs: Any) -> KernelConnectionInfo:
        """Launch a kernel with a command."""
        scrubbed_kwargs = LocalProvisioner._scrub_kwargs(kwargs)

        # Setup required directories and mounts
        chroot_path = "/tmp/workspaces"

        # Add /code to required dirs for connection file
        required_dirs = [
            "/usr/bin",
            "/usr/lib",
            "/usr/lib/python3.10",
            "/usr/local/lib/python3.10",
            "/lib",
            "/lib/aarch64-linux-gnu",
            "/code",  # Add this for connection file
        ]

        # Create directory structure
        for dir_path in required_dirs:
            full_path = os.path.join(chroot_path, dir_path.lstrip("/"))
            logger.info(f"Creating directory: {full_path}")
            os.makedirs(full_path, exist_ok=True)

        mount_points = [
            # Core system directories
            ("/lib", f"{chroot_path}/lib"),
            ("/lib/aarch64-linux-gnu", f"{chroot_path}/lib/aarch64-linux-gnu"),
            ("/usr/lib", f"{chroot_path}/usr/lib"),
            ("/usr/bin", f"{chroot_path}/usr/bin"),
            # Python specific directories
            ("/usr/lib/python3.10", f"{chroot_path}/usr/lib/python3.10"),
            ("/usr/local/lib/python3.10", f"{chroot_path}/usr/local/lib/python3.10"),
            # Add mount for /code directory
            ("/code", f"{chroot_path}/code"),
        ]

        try:
            # Mount directories
            for src, dest in mount_points:
                if os.path.exists(src):
                    result = os.system(f"mount --bind {src} {dest}")
                    if result == 0:
                        logger.info(f"Successfully mounted {src} to {dest}")
                    else:
                        logger.error(f"Failed to mount {src} to {dest}. Return code: {result}")
                else:
                    logger.warning(f"Source path does not exist: {src}")

            # Modify the command to use absolute path for connection file
            cmd_str = " ".join(cmd)

            if "-f" in cmd_str:
                connection_file = cmd[cmd.index("-f") + 1]
                # Make sure the path is relative to the chroot
                new_connection_file = os.path.join("/code", os.path.basename(connection_file))
                cmd[cmd.index("-f") + 1] = new_connection_file

            logger.info(f"Launching kernel with command: {['/usr/sbin/chroot', chroot_path] + cmd}")
            self.process = launch_kernel(["/usr/sbin/chroot", chroot_path] + cmd, **scrubbed_kwargs)

            # Start monitoring process output
            def log_output():
                while True:
                    if self.process.stdout:
                        output = self.process.stdout.readline()
                        if output:
                            logger.info(f"Kernel output: {output.decode().strip()}")
                    if self.process.stderr:
                        error = self.process.stderr.readline()
                        if error:
                            logger.error(f"Kernel error: {error.decode().strip()}")
                    if self.process.poll() is not None:
                        break

            import threading

            output_thread = threading.Thread(target=log_output, daemon=True)
            output_thread.start()

            return self.connection_info

        finally:
            # Cleanup mounts when done
            for _, dest in mount_points[::-1]:  # Unmount in reverse order
                if os.path.ismount(dest):
                    logger.info(f"Unmounting {dest}")
                    result = os.system(f"umount {dest}")
                    if result != 0:
                        logger.error(f"Failed to unmount {dest}. Return code: {result}")
