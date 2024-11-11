() => {
  window["clearTags"] = () => {
    const tags = document.querySelectorAll('[id^="__llmstack-"]');
    tags.forEach((tag) => tag.remove());
  };

  const addBoundingBox = (element, tag) => {
    const text = document.createElement("div");
    text.id = "__llmstack-" + tag;
    text.textContent = tag;
    text.style.position = "absolute";
    text.style.top = element.offsetTop + "px";
    text.style.left = element.offsetLeft + "px";
    text.style.color = "red";
    text.style.fontSize = "12px";
    text.style.backgroundColor = "white";

    const locatorParent = element.parentElement;
    locatorParent ? locatorParent.appendChild(text) : element.appendChild(text);
  };

  const skipElement = (el) => {
    // Check for zero dimensions, disabled state, and non-interactive tags
    if (
      el.offsetWidth === 0 ||
      el.offsetHeight === 0 ||
      el.disabled ||
      el.tagName === "SCRIPT" ||
      el.tagName === "STYLE"
    ) {
      return true;
    }

    // Get computed style to check visibility and display properties
    const style = window.getComputedStyle(el);
    if (style.visibility === "hidden" || style.display === "none") {
      return true;
    }

    // Check if the element or its parent is hidden
    if (
      el.offsetParent === null ||
      el.offsetParent.tagName === "DETAILS" ||
      el.offsetParent.tagName === "SUMMARY"
    ) {
      return true;
    }

    // If element is an input, handle non interactive types
    if (el.tagName === "INPUT") {
      const type = el.type.toLowerCase();
      if (
        type === "hidden" ||
        type === "radio" ||
        type === "checkbox" ||
        type === "file" ||
        type === "submit" ||
        type === "reset" ||
        type === "button" ||
        type === "image"
      ) {
        return true;
      }
    }

    // Include interactive divs
    if (el.tagName === "DIV") {
      const role = el.getAttribute("role");
      if (
        role !== "button" &&
        role !== "link" &&
        role !== "checkbox" &&
        role !== "textbox"
      ) {
        return true;
      }
    }

    return false;
  };

  const isClickable = (el) => {
    // Check if the element is clickable
    const style = window.getComputedStyle(el);
    if (style.cursor === "pointer") {
      return true;
    }

    // Check if the element is an input
    if (el.tagName === "INPUT") {
      const type = el.type.toLowerCase();
      if (type === "submit" || type === "reset" || type === "button") {
        return true;
      }
    }

    // Check if the element is a button
    if (el.tagName === "BUTTON") {
      return true;
    }

    // Check if the element is an anchor
    if (el.tagName === "A") {
      return true;
    }

    // Check if the element is a div with a role
    if (el.tagName === "DIV") {
      const role = el.getAttribute("role");
      if (
        role === "button" ||
        role === "link" ||
        role === "checkbox" ||
        role === "textbox"
      ) {
        return true;
      }
    }

    // Check if the element is a label
    if (el.tagName === "LABEL") {
      return true;
    }

    return false;
  };

  const isEditable = (el) => {
    // Check if the element is an input
    if (el.tagName === "INPUT") {
      const type = el.type.toLowerCase();
      if (type === "text" || type === "password" || type === "email") {
        return true;
      }
    }

    // Check if the element is a textarea
    if (el.tagName === "TEXTAREA") {
      return true;
    }

    // Check if the element is a div with a role
    if (el.tagName === "DIV") {
      const role = el.getAttribute("role");
      if (role === "textbox" && el.getAttribute("contenteditable") === "true") {
        return true;
      }
    }

    return false;
  };

  const isElementinViewport = (el) => {
    // Check if the element is in the viewport
    const rect = el.getBoundingClientRect();
    if (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    ) {
      return true;
    }
    return false;
  };

  window["addTags"] = (selectors = ["text"], annotate = false) => {
    // Clear existing tags
    window["clearTags"]();

    // Get text from the page
    const text = document.body?.innerText;

    const getAllElements = (selector, annotate) => {
      return Array.from(document.querySelectorAll(selector))
        .map((element, index) => {
          // Skip if the element is disabled or not visible
          if (skipElement(element)) return null;

          let tag = `${selector.slice(0, 1)}=${index}`;
          if (selector === "textarea") {
            tag = `ta=${index}`;
          } else if (selector === "input") {
            tag = `in=${index}`;
          }

          if (annotate) {
            addBoundingBox(element, tag);
          }
          const rect = element.getBoundingClientRect();
          return {
            text:
              element.textContent.trim() || element.alt || element.title || "",
            type: element.type || "",
            url: element.href || "",
            tag: tag,
            clickable: isClickable(element),
            editable: isEditable(element),
            src: element.src || "",
            inViewport: isElementinViewport(element),
            boundingBox: {
              top: rect.top,
              left: rect.left,
              width: rect.width,
              height: rect.height,
            },
            midpoint: {
              x: rect.left + rect.width / 2,
              y: rect.top + rect.height / 2,
            },
          };
        })
        .filter((el) => el !== null);
    };

    let output = {
      text: text,
    };

    output["buttons"] = selectors.includes("button")
      ? getAllElements("button", annotate)
      : [];
    output["inputs"] = selectors.includes("input")
      ? getAllElements("input", annotate)
      : [];
    output["selects"] = selectors.includes("select")
      ? getAllElements("select", annotate)
      : [];
    output["textareas"] = selectors.includes("textarea")
      ? getAllElements("textarea", annotate)
      : [];
    output["links"] = selectors.includes("a")
      ? getAllElements("a", annotate)
      : [];
    output["labels"] = selectors.includes("label")
      ? getAllElements("label", annotate)
      : [];
    output["divs"] = selectors.includes("div")
      ? getAllElements("div", annotate)
      : [];
    output["images"] = selectors.includes("img")
      ? getAllElements("img", annotate)
      : [];

    return output;
  };
};
