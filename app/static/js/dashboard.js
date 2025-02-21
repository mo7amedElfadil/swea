if (!window.dashboardInitialized) {
  window.dashboardInitialized = true; // Prevent multiple executions

  const tabsContainer = document.body;

  // Update the active tab visually
  const updateActiveTab = (activeTab) => {
    document
      .querySelectorAll("[role='tab']")
      .forEach((tab) =>
        tab.setAttribute("aria-selected", tab === activeTab ? "true" : "false"),
      );
  };

  // Save the active tab to localStorage
  const saveActiveTabToLocalStorage = (queryParam) =>
    localStorage.setItem("activeTabQuery", queryParam);

  // Restore the active tab from localStorage
  const restoreActiveTabFromLocalStorage = () => {
    const savedQuery = localStorage.getItem("activeTabQuery");
    if (savedQuery) {
      const activeTab = [...document.querySelectorAll("[role='tab']")].find(
        (tab) => tab.getAttribute("hx-get")?.includes(savedQuery),
      );
      if (activeTab) {
        updateActiveTab(activeTab);
        htmx.ajax("GET", activeTab.getAttribute("hx-get"), {
          target: activeTab.getAttribute("hx-target"),
          swap: activeTab.getAttribute("hx-swap"),
          headers: { "hx-tab": "true" },
        });
      }
    }
  };

  // Handle tab clicks using event delegation
  tabsContainer.addEventListener("click", (event) => {
    const tab = event.target.closest("[role='tab']");
    if (tab) {
      const queryParam = tab.getAttribute("hx-get").split("?q=")[1];
      saveActiveTabToLocalStorage(queryParam);
      updateActiveTab(tab);
    }
  });

  // Listen to HTMX requests to update the active tab
  tabsContainer.addEventListener("htmx:beforeSwap", (event) => {
    if (event.detail.xhr.getResponseHeader("hx-tab")) {
      const queryParam = event.detail.requestConfig.parameters.q;
      const activeTab = [...document.querySelectorAll("[role='tab']")].find(
        (tab) => tab.getAttribute("hx-get")?.includes(queryParam),
      );
      if (activeTab) {
        saveActiveTabToLocalStorage(queryParam);
        updateActiveTab(activeTab);
      }
    }
  });

  // Handle language switch
  document.addEventListener("htmx:afterRequest", (evt) => {
    const path = evt.detail.pathInfo.requestPath;
    if (path.match("set_language") && evt.detail.successful) {
      restoreActiveTabFromLocalStorage();
    }
  });

  // Loading indicator for HTMX requests
  const toggleLoadingIndicator = (show) =>
    document
      .getElementById("loading-indicator")
      .classList.toggle("htmx-request", show);

  tabsContainer.addEventListener("htmx:configRequest", () =>
    toggleLoadingIndicator(true),
  );
  tabsContainer.addEventListener("htmx:afterRequest", () =>
    toggleLoadingIndicator(false),
  );

  // Restore the active tab on page load
  restoreActiveTabFromLocalStorage();
}
