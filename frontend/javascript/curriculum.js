import '../styles/curriculum.scss'

document.addEventListener('DOMContentLoaded', () => {
  const select = document.querySelector('#typeform select')

  select?.addEventListener('change', () => {
    document.querySelector('#typeform').submit()
  })
})