// helper: erstellt ein SVG-Element mit Heroicon „arrows-pointing-out“
function createFullscreenIcon() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "1em");
    svg.setAttribute("height", "1em");
    svg.setAttribute("stroke-width", "1.5");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");

    // Pfad aus Heroicons v2.1.1 outline (arrows-pointing-out.svg) :contentReference[oaicite:0]{index=0}
    svg.innerHTML = `
      <path d="M4.5 9.75V4.5h5.25M4.5 4.5l6 6
               M14.25 4.5h5.25v5.25M19.5 4.5l-6 6
               M19.5 14.25v5.25h-5.25M19.5 19.5l-6-6
               M9.75 19.5H4.5v-5.25M4.5 19.5l6-6" />
    `;
    return svg;
}


function addToModbar() {
    const modeBars = document.querySelectorAll(".modebar-container");
    for(let i=0; i<modeBars.length; i++) {
        const modeBarGroups = modeBars[i].querySelectorAll(".modebar-group");
        const modeBarBtns = modeBarGroups[modeBarGroups.length - 1].querySelectorAll(".modebar-btn");

        if (modeBarBtns[modeBarBtns.length - 1].getAttribute('data-title') !== 'Fullscreen') {
            const aTag = document.createElement('a');
            aTag.className = "modebar-btn";
            aTag.setAttribute("rel", "tooltip");
            aTag.setAttribute("data-title", "Fullscreen");
            aTag.setAttribute("style", "color:gray");
            aTag.setAttribute("onClick", "fullscreen(this);");
            const iTag = createFullscreenIcon();
            aTag.appendChild(iTag);
            modeBarGroups[modeBarGroups.length - 1].appendChild(aTag);
        }
    }
}

function fullscreen(el) {
    elem = el.closest('.dash-graph');
    if (document.fullscreenElement) {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { // Firefox
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { // IE/Edge
            document.msExitFullscreen();
        }
    }
    else {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) { // Firefox
            elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) { // Chrome, Safari and Opera
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { // IE/Edge
            elem.msRequestFullscreen();
        }
    }
}

window.fetch = new Proxy(window.fetch, {
    apply(fetch, that, args) {
        // Forward function call to the original fetch
        const result = fetch.apply(that, args);

        // Do whatever you want with the resulting Promise
        result.then((response) => {
            if (args[0] == '/_dash-update-component') {
                setTimeout(function() {addToModbar()}, 1000)
            }})
        return result
        }
})