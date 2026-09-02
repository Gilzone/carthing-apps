/* Car Thing: don't let the overlay eat taps; turn touch into mouse for Construct/Ruffle games. */
(function () {
  if (window.__ctTouchFix) return;
  window.__ctTouchFix = true;

  var css = document.createElement("style");
  css.textContent =
    "#ct-hud .bar{pointer-events:none!important;width:auto!important}" +
    "#ct-home,#ct-hud .chip,#ct-hud .btn,#ct-stick,#ct-look,#ct-hud .row,#ct-hud .hot,#ct-hud .btns{pointer-events:auto!important}";
  (document.head || document.documentElement).appendChild(css);

  if (/amongus\.html/i.test(location.pathname || "")) return;

  function hudHit(el) {
    return !!(el && el.closest && el.closest("#ct-home, #ct-hud .chip, #ct-hud .btn, #ct-stick, #ct-look, #ct-hud .row, #ct-hud .hot, #ct-hud .btns"));
  }
  function canvas() {
    return document.querySelector("canvas") || document.querySelector("ruffle-player") || document.body || document;
  }
  var synthing = false;
  var lastPtr = 0;
  function fire(type, x, y, buttons, button) {
    if (synthing) return;
    synthing = true;
    try {
      var t = canvas();
      var init = {
        bubbles: true, cancelable: true, composed: true, view: window,
        clientX: x, clientY: y, pageX: x, pageY: y, screenX: x, screenY: y,
        pointerId: 1, pointerType: "mouse", isPrimary: true,
        button: button < 0 ? 0 : button, buttons: buttons, width: 1, height: 1,
        pressure: buttons ? 0.5 : 0
      };
      var pev = new PointerEvent(type, init);
      try {
        Object.defineProperty(pev, "pointerType", { get: function () { return "mouse"; } });
        Object.defineProperty(pev, "pointerId", { get: function () { return 1; } });
      } catch (e) {}
      t.dispatchEvent(pev);
      var mt = { pointerdown: "mousedown", pointermove: "mousemove", pointerup: "mouseup", pointercancel: "mouseup" }[type];
      if (mt) {
        t.dispatchEvent(new MouseEvent(mt, {
          bubbles: true, cancelable: true, view: window,
          clientX: x, clientY: y, button: button < 0 ? 0 : button, buttons: buttons
        }));
      }
    } finally {
      synthing = false;
    }
  }
  function fromPointer(e) {
    if (e.pointerType === "mouse") return;
    if (hudHit(e.target)) return;
    lastPtr = performance.now();
    var up = e.type === "pointerup" || e.type === "pointercancel";
    fire(e.type, e.clientX, e.clientY, up ? 0 : 1, e.type === "pointermove" ? -1 : 0);
  }
  window.addEventListener("pointerdown", fromPointer, true);
  window.addEventListener("pointermove", fromPointer, true);
  window.addEventListener("pointerup", fromPointer, true);
  window.addEventListener("pointercancel", fromPointer, true);
  function fromTouch(type, e) {
    if (performance.now() - lastPtr < 80) return;
    if (hudHit(e.target)) return;
    var t = e.changedTouches && e.changedTouches[0];
    if (!t) return;
    var up = type === "pointerup";
    fire(type, t.clientX, t.clientY, up ? 0 : 1, type === "pointermove" ? -1 : 0);
  }
  window.addEventListener("touchstart", function (e) { fromTouch("pointerdown", e); }, true);
  window.addEventListener("touchmove", function (e) { fromTouch("pointermove", e); }, true);
  window.addEventListener("touchend", function (e) { fromTouch("pointerup", e); }, true);
  window.addEventListener("touchcancel", function (e) { fromTouch("pointerup", e); }, true);
})();
