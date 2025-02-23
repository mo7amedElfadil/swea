if (!window.dashboardInitialized) {
  window.dashboardInitialized = true; // Prevent multiple executions
  const nodes = [];
  const add = (template) => (evt) => {
    const clone = template.content.cloneNode(true);
    const container = document.getElementById('contents');

    nodes.push(clone);
    clone.querySelector('#add-template').addEventListener('click', add(template));
    clone.querySelector('#remove-template').addEventListener('click', remove);

    for (let i = 0; i < nodes.length; i++) {
      const elem = nodes[i].querySelector('div');

      if (elem && !elem.hasAttribute('id')) {
        elem.setAttribute('id', i);
        elem.querySelector('textarea[name="content[ar]"]').setAttribute('name', `content[${i}][ar]`);
        elem.querySelector('textarea[name="content[en]"]').setAttribute('name', `content[${i}][en]`);
        elem.prepend(generate_title(i + 1));
      }
    }
    container.appendChild(clone);
    const secondToLast = container.children[container.children.length - 2];
    secondToLast.querySelector('#add-template').classList.add('hidden')
  };

  const remove = (evt) => {
    const id = evt.currentTarget.parentElement.parentElement.getAttribute('id');
    const container = document.getElementById('contents');
    nodes.splice(parseInt(id), 1);
    evt.currentTarget.parentElement.parentElement.remove();
    if (nodes.length == 1) {
      container.children[2].querySelector('#add-template').classList.remove('hidden')
    } else if (nodes.length == 0) {
      container.children[0].querySelector('#add-more').classList.remove('hidden')
    }
  };

  function generate_title(id) {
    const label = document.createElement('label');
    label.textContent = `Content ${id}`;
    label.setAttribute('class', 'text-sm font-medium text-gray-700 capitalize')
    return label;
  }

  const observer = new MutationObserver(function(mutationsList, observer) {
    if (document.getElementById('contents')) {
      const addMore = document.getElementById('add-more');

      addMore.addEventListener('click', () => {
        const template = document.getElementById('content-template');
        const container = document.getElementById('contents');
        const clone = template.content.cloneNode(true);

        clone.querySelector('#add-template').addEventListener('click', add(template));
        clone.querySelector('#remove-template').addEventListener('click', remove);
        clone.querySelector('div').setAttribute('id', 0);
        clone.querySelector('textarea[name="content[ar]"]').setAttribute('name', 'content[0][ar]');
        clone.querySelector('textarea[name="content[en]"]').setAttribute('name', 'content[0][en]');
        clone.querySelector('div').prepend(generate_title(1));
        addMore.classList.add('hidden');
        nodes.push(clone);
        container.appendChild(clone);
      });

      observer.disconnect(); // Stop observing once the node is found
    }
  });

  // Start observing for changes in the DOM
  observer.observe(document.body, { childList: true, subtree: true });

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
