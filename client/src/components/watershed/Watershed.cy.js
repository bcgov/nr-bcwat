import Watershed from '@/components/watershed/Watershed.vue'

describe('<Watershed />', () => {
  it('renders', () => {
    // see: https://on.cypress.io/mounting-vue
    cy.mount(Watershed)
  })
})
