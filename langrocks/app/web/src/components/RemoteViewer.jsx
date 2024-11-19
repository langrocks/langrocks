import RFB from "@novnc/novnc/lib/rfb";
import React from "react";
import { useSearchParams } from "react-router-dom";
import { useCallback, useEffect, useRef, useState } from "react";

export default function RemoteViewer() {
  const [searchParams] = useSearchParams();
  const screenRef = useRef(null);
  const boxRef = useRef(null);
  const rfbRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [closedConnection, setClosedConnection] = useState(false);
  const isMobile = window.innerWidth < 768;

  const wsUrl = `${searchParams.get("wsProtocol")}://${searchParams.get("username")}:${searchParams.get("password")}@${searchParams.get("hostname")}:${searchParams.get("port") || 80}/${searchParams.get("path") || ""}?token=${searchParams.get("token")}`;

  console.log("wsUrl", wsUrl);

  const setupRFB = useCallback(() => {
    if (screenRef.current && !rfbRef.current) {
      const credentials = wsUrl.split("@")[0].split("://")[1];

      rfbRef.current = new RFB(screenRef.current, wsUrl, {
        credentials: {
          username: credentials.split(":")[0],
          password: credentials.split(":")[1],
        },
        scaleViewport: true,
      });

      rfbRef.current.addEventListener("connect", () => {
        console.log("Connected");
        setConnected(true);
      });

      rfbRef.current.addEventListener("disconnect", () => {
        setConnected(false);
        setClosedConnection(true);
      });

      rfbRef.current.addEventListener("credentialsrequired", () => {
        console.log("Credentials required");
      });

      rfbRef.current.addEventListener("securityfailure", () => {
        console.log("Security failure");
      });

      rfbRef.current.addEventListener("capabilities", () => {
        console.log("Capabilities");
      });

      rfbRef.current.addEventListener("clipboard", (e) => {
        if (e.detail.text) {
          navigator.clipboard.writeText(e.detail.text);
        }
      });

      rfbRef.current.addEventListener("bell", () => {
        console.log("Bell");
      });

      rfbRef.current.addEventListener("desktopname", () => {
        console.log("Desktop name");
      });

      rfbRef.current.addEventListener("resize", () => {
        console.log("Resize");
      });

      rfbRef.current.addEventListener("focus", () => {
        console.log("Focus");
      });

      rfbRef.current.addEventListener("blur", () => {
        console.log("Blur");
      });
    }
  }, [wsUrl]);

  useEffect(() => {
    if (!wsUrl || rfbRef.current) {
      return;
    }

    // Try to setup RFB every second until it works with a timeout of 10 seconds
    let tries = 0;
    const interval = setInterval(() => {
      if (!rfbRef.current) {
        setupRFB();
        tries++;
      }

      if (tries >= 10 || rfbRef.current) {
        if (rfbRef.current && screenRef.current) {
          rfbRef.current.viewOnly = true;

          // Get width of screenRef parent and set it to the screenRef
          const width =
            isMobile || screenRef.current.clientWidth > 400
              ? screenRef.current.clientWidth
              : 400;
          screenRef.current.style.width = `${width}px`;
          screenRef.current.style.height = `${(width * 720) / 1024}px`;

          rfbRef.current.scaleViewport = true;
          rfbRef.current.showDotCursor = true;
        }
        clearInterval(interval);
      }
    }, 1000);
  }, [wsUrl, setupRFB, isMobile]);

  useEffect(() => {
    if (closedConnection && rfbRef.current) {
      screenRef.current.innerHTML = "Video stream ended";
      screenRef.current.style.height = "30px";
    }
  }, [closedConnection]);

  return (
    <div ref={boxRef} style={{ width: "100%" }}>
      <div ref={screenRef}></div>
      {!connected &&
        !closedConnection &&
        "Loading video stream. Make sure you have stream video option set."}
    </div>
  );
}
