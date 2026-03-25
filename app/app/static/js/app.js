const TRUSTED_NAVIGATION_KEY = "les_viviers_trusted_navigation";

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

function registerTrustedNavigationSources() {
    document.querySelectorAll("a[href]").forEach((link) => {
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
    });

    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            setTrustedNavigation();
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const isProtectedPage = document.body.classList.contains("app-body");

    if (isProtectedPage && !enforceLoginAsEntryPoint()) {
        return;
    }

    registerTrustedNavigationSources();

    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (!sidebar || !toggle) {
        return;
    }

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("sidebar-open");
    });
});
