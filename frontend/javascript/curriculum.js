import '../styles/curriculum.scss';

document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('#kindform select').addEventListener('change', () => {
    document.querySelector('#kindform').submit()
  })
})