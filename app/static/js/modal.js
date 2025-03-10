export const MODAL = {
  clone: null,
  showModal,
  hideModal,
}

function showModal() {
  const modalTemplate = document.getElementById('modal-template')
  MODAL.clone = modalTemplate.content.cloneNode(true)
  MODAL.container = MODAL.clone.querySelector('#default-modal')
  MODAL.header = MODAL.clone.querySelector('#modal-header')
  MODAL.body = MODAL.clone.querySelector('#modal-body')
  MODAL.footer = MODAL.clone.querySelector('#modal-footer')
  MODAL.close = MODAL.clone.querySelector('#modal-close')
  MODAL.cancel = MODAL.clone.querySelector('#modal-cancel')

  document.body.appendChild(MODAL.clone)
}

function hideModal() {
  MODAL.close.addEventListener('click', () => {
    console.log('close')
    MODAL.container.remove()
  })
  MODAL.close.addEventListener('click', () => {
    MODAL.container.remove()
  })

  document.addEventListener('click', (evt) => {
    if (
      !MODAL.header.contains(evt.target) &&
      !MODAL.body.contains(evt.target) &&
      !MODAL.footer.contains(evt.target) &&
      !document.getElementById('modal-toggle').contains(evt.target)
    ) {
      //modal.classList.add('hidden')
      MODAL.container.remove()
    }
  })

  MODAL.container.addEventListener('htmx:afterRequest', (evt) => {
    if (evt.detail.successful) {
      MODAL.container.remove()
    }
  })
}
