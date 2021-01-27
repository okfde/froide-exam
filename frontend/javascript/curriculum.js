import '../styles/curriculum.scss'

document.addEventListener('DOMContentLoaded', () => {
  const typeform = document.querySelector('#typeform select')

  typeform && typeform.addEventListener('change', () => {
    typeform.submit()
  })
})