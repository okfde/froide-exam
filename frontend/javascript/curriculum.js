import '../styles/curriculum.scss';

document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('#typeform select').addEventListener('change', () => {
    document.querySelector('#typeform').submit()
  })
})