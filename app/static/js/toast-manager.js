// static/js/toast-manager.js
class ToastManager {
  constructor() {
    this.toastContainer = document.getElementById('toast-container')

    // If container doesn't exist, create one based on document direction
    if (!this.toastContainer) {
      this.toastContainer = document.createElement('div')
      this.toastContainer.id = 'toast-container'

      // Check if the document is RTL
      const isRTL =
        document.documentElement.dir === 'rtl' ||
        document.body.getAttribute('dir') === 'rtl' ||
        document.documentElement.lang === 'ar'

      // Position based on RTL/LTR
      this.toastContainer.className = `fixed top-4 flex flex-col gap-2 z-[500]`
      this.toastContainer.style.transform = 'translate(-50%, 0)'
      this.toastContainer.style.left = '50%'
      document.body.appendChild(this.toastContainer)
    }

    // Ensure listeners are not added multiple times
    if (!this.listenersAdded) {
      // This event can be dispatched to show a toast from JS but when the toast
      // triggered from the end-point with `add_toast`, it will show an overlapping toast
      // document.addEventListener('show-toast', (e) =>
      //     this.showToast(e.detail)
      // )
      document.addEventListener('htmx:afterRequest', (e) => {
        const toastHeader = e.detail.xhr.getResponseHeader('HX-Trigger')
        console.log({ showToast: !!toastHeader });
        if (toastHeader) {
          try {
            const triggers = JSON.parse(toastHeader)
            if (triggers.showToast) {
              this.showToast(triggers.showToast)
            }
          } catch (e) {
            console.error('Error parsing HX-Trigger header', e)
          }
        }
      })
      this.listenersAdded = true
    }
  }

  async showToast({ type = 'success', message = '', duration = 10000 }) {
    // Check if a toast with the same message already exists
    const existingToast = Array.from(this.toastContainer.children).find(
      (toast) =>
        toast.querySelector('.text-sm.font-normal')?.textContent ===
        message
    )
    if (existingToast) {
      return
    }
    // Load the appropriate toast template via fetch if not already cached
    if (!this[`${type}Template`]) {
      const response = await fetch(`/toast/${type}`)
      this[`${type}Template`] = await response.text()
    }

    // Create a new toast element
    const toastEl = document.createElement('div')
    toastEl.innerHTML = this[`${type}Template`]
    const toast = toastEl.firstElementChild

    // Set the message
    const messageEl = toast.querySelector('.text-sm.font-normal')
    if (messageEl) {
      messageEl.textContent = message
    }

    // Check for RTL text
    const isRTL =
      document.documentElement.dir === 'rtl' ||
      document.body.getAttribute('dir') === 'rtl' ||
      document.documentElement.lang === 'ar'

    // Apply RTL-specific classes if needed
    if (isRTL && toast) {
      // Make sure text alignment is correct for RTL
      messageEl?.classList.add('text-right')

      // Flip any directional margins from ms- to me- for RTL
      Array.from(toast.querySelectorAll('[class*="ms-"]')).forEach(
        (el) => {
          const classes = Array.from(el.classList)
          classes.forEach((cls) => {
            if (cls.startsWith('ms-')) {
              const value = cls.replace('ms-', '')
              el.classList.remove(cls)
              el.classList.add(`me-${value}`)
            }
          })
        }
      )
    }

    // Set a unique ID
    const uniqueId = `toast-${Date.now()}-${Math.floor(Math.random() * 1000)}`
    toast.id = uniqueId

    // Add dismiss handler
    const dismissBtn = toast.querySelector('button')
    if (dismissBtn) {
      dismissBtn.addEventListener('click', () => this.dismissToast(toast))
      dismissBtn.setAttribute('data-dismiss-target', `#${uniqueId}`)
    }

    // Add to container and animate in
    toast.classList.add(
      'opacity-0',
      'translate-y-4',
      'transition-all',
      'duration-300'
    )
    this.toastContainer.appendChild(toast)

    // Trigger reflow to ensure animation works
    void toast.offsetWidth

    // Show toast
    toast.classList.remove('opacity-0', 'translate-y-4')

    // Auto dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        this.dismissToast(toast)
      }, duration)
    }

    return toast
  }

  dismissToast(toast) {
    if (!toast || !toast.isConnected) return

    // Animate out
    toast.classList.add('opacity-0', 'translate-y-4')

    // Remove after animation completes
    setTimeout(() => {
      if (toast.isConnected) {
        toast.remove()
      }
    }, 300)
  }
}

// Initialize the toast manager
if (!window.toastManager) {
  document.addEventListener('DOMContentLoaded', () => {
    window.toastManager = new ToastManager()
  })
}

// Helper function to show toast from JS
function showToast(options) {
  document.dispatchEvent(
    new CustomEvent('show-toast', {
      detail: options,
    })
  )
}
