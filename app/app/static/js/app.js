const TRUSTED_NAVIGATION_KEY = "les_viviers_trusted_navigation";
let autoRefreshTimerId = null;
let autoRefreshInFlight = false;

function isSameOriginLink(link) {
    try {
        return new URL(link.href, window.location.origin).origin === window.location.origin;
    } catch (error) {
        return false;
    }
}

function setTrustedNavigation() {
    window.sessionStorage.setItem(TRUSTED_NAVIGATION_KEY, "1");
}

function consumeTrustedNavigation() {
    const isTrusted = window.sessionStorage.getItem(TRUSTED_NAVIGATION_KEY) === "1";
    window.sessionStorage.removeItem(TRUSTED_NAVIGATION_KEY);
    return isTrusted;
}

function enforceLoginAsEntryPoint() {
    const navigationEntry = window.performance.getEntriesByType("navigation")[0];
    const navigationType = navigationEntry ? navigationEntry.type : "navigate";
    const isTrustedNavigation = consumeTrustedNavigation();

    if (navigationType === "reload" || navigationType === "back_forward" || !isTrustedNavigation) {
        window.location.replace("/logout");
        return false;
    }

    return true;
}

function registerTrustedNavigationSources(root = document) {
    root.querySelectorAll("a[href]").forEach((link) => {
        if (link.dataset.trustedNavigationBound === "1") {
            return;
        }

        if (!isSameOriginLink(link) || (link.target && link.target !== "_self")) {
            return;
        }

        link.addEventListener("click", () => {
            if (new URL(link.href, window.location.origin).pathname === "/logout") {
                window.sessionStorage.removeItem(TRUSTED_NAVIGATION_KEY);
                return;
            }

            setTrustedNavigation();
        });

        link.dataset.trustedNavigationBound = "1";
    });

    root.querySelectorAll("form").forEach((form) => {
        if (form.dataset.trustedNavigationBound === "1") {
            return;
        }

        form.addEventListener("submit", () => {
            setTrustedNavigation();
        });

        form.dataset.trustedNavigationBound = "1";
    });
}

function shouldPauseAutoRefresh() {
    if (document.visibilityState !== "visible") {
        return true;
    }

    const activeElement = document.activeElement;

    if (!activeElement) {
        return false;
    }

    return activeElement.matches("input, textarea, select");
}

function replacePageShell(nextDocument) {
    const currentPageShell = document.getElementById("pageShell");
    const nextPageShell = nextDocument.getElementById("pageShell");

    if (!currentPageShell || !nextPageShell) {
        return false;
    }

    currentPageShell.innerHTML = nextPageShell.innerHTML;
    currentPageShell.dataset.autoRefreshSeconds = nextPageShell.dataset.autoRefreshSeconds || "0";
    document.title = nextDocument.title;
    registerTrustedNavigationSources(currentPageShell);
    return true;
}

async function refreshProtectedPageSilently() {
    const pageShell = document.getElementById("pageShell");

    if (!pageShell || autoRefreshInFlight || shouldPauseAutoRefresh()) {
        return;
    }

    autoRefreshInFlight = true;

    try {
        const response = await window.fetch(
            `${window.location.pathname}${window.location.search}`,
            {
                credentials: "same-origin",
                headers: {
                    "Cache-Control": "no-cache",
                    "X-Requested-With": "XMLHttpRequest",
                },
            },
        );

        const markup = await response.text();
        const nextDocument = new window.DOMParser().parseFromString(markup, "text/html");

        if (!nextDocument.body.classList.contains("app-body")) {
            window.location.replace("/logout");
            return;
        }

        replacePageShell(nextDocument);
    } catch (error) {
        window.console.error("Auto-refresh impossible", error);
    } finally {
        autoRefreshInFlight = false;
    }
}

function setupAutoRefresh() {
    const pageShell = document.getElementById("pageShell");
    const refreshSeconds = Number(pageShell?.dataset.autoRefreshSeconds || "0");

    if (!pageShell || !Number.isFinite(refreshSeconds) || refreshSeconds <= 0) {
        return;
    }

    if (autoRefreshTimerId) {
        window.clearInterval(autoRefreshTimerId);
    }

    autoRefreshTimerId = window.setInterval(() => {
        refreshProtectedPageSilently();
    }, refreshSeconds * 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    const isProtectedPage = document.body.classList.contains("app-body");

    if (isProtectedPage && !enforceLoginAsEntryPoint()) {
        return;
    }

    registerTrustedNavigationSources();
    setupAutoRefresh();

    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (!sidebar || !toggle) {
        return;
    }

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("sidebar-open");
    });
});
