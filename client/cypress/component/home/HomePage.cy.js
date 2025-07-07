import HomePage from "@/components/home/HomePage.vue";

describe('<HomePage />', () => {
    it('mounts and lists pages', () => {
        cy.mount(HomePage);
        cy.get('.q-list').children().should('have.length', 6);
    });
});
