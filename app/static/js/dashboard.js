if (!window.dashboardInitialized) {
    window.dashboardInitialized = true // Prevent multiple executions
    const tabsContainer = document.body

    // Update the active tab visually
    const updateActiveTab = (activeTab) => {
        document
            .querySelectorAll("[role='db-tab']")
            .forEach((tab) =>
                tab.setAttribute(
                    'aria-selected',
                    tab === activeTab ? 'true' : 'false'
                )
            )
    }

    // Save the active tab to localStorage
    const saveActiveTabToLocalStorage = (queryParam) =>
        localStorage.setItem('activeTabQuery', queryParam)

    // Restore the active tab from localStorage
    const restoreActiveTabFromLocalStorage = () => {
        const savedQuery = localStorage.getItem('activeTabQuery')
        if (savedQuery) {
            const activeTab = [
                ...document.querySelectorAll("[role='db-tab']"),
            ].find((tab) => tab.getAttribute('hx-get')?.includes(savedQuery))
            if (activeTab) {
                updateActiveTab(activeTab)
                htmx.ajax('GET', activeTab.getAttribute('hx-get'), {
                    target: activeTab.getAttribute('hx-target'),
                    swap: activeTab.getAttribute('hx-swap'),
                    headers: { 'hx-tab': 'true' },
                })
            }
        }
    }

    // Handle tab clicks using event delegation
    tabsContainer.addEventListener('click', (event) => {
        const tab = event.target.closest("[role='db-tab']")
        if (tab) {
            const queryParam = tab.getAttribute('hx-get').split('?q=')[1]
            saveActiveTabToLocalStorage(queryParam)
            updateActiveTab(tab)
        }
    })

    // Listen to HTMX requests to update the active tab
    tabsContainer.addEventListener('htmx:beforeSwap', (event) => {
        if (event.detail.xhr.getResponseHeader('hx-tab')) {
            const queryParam = event.detail.requestConfig.parameters.q
            const activeTab = [
                ...document.querySelectorAll("[role='db-tab']"),
            ].find((tab) => tab.getAttribute('hx-get')?.includes(queryParam))
            if (activeTab) {
                saveActiveTabToLocalStorage(queryParam)
                updateActiveTab(activeTab)
            }
        }
    })

    // Handle language switch
    document.addEventListener('htmx:afterRequest', (evt) => {
        const path = evt.detail.pathInfo.requestPath
        if (path.match('set_language') && evt.detail.successful) {
            restoreActiveTabFromLocalStorage()
        }
    })

    // Restore the active tab on page load
    restoreActiveTabFromLocalStorage()
}

document.body.addEventListener('htmx:beforeRequest', (e) => {
    if (e.target.getAttribute('hx-target') === '#tab-content') {
        document.getElementById('tab-loader')?.classList.remove('hidden')
        document.getElementById('tab-content')?.classList.add('opacity-50')
    }
})

document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.target.id === 'tab-content') {
        document.getElementById('tab-loader')?.classList.add('hidden')
        document.getElementById('tab-content')?.classList.remove('opacity-50')
        document.getElementById('tab-content')?.classList.add('animate-fade-in')
    }
})

document.body.addEventListener('htmx:beforeSwap', (e) => {
    // Reset animation class before new content is inserted
    document.getElementById('tab-content')?.classList.remove('animate-fade-in')
})
