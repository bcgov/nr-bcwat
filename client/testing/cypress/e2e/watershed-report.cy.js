import watershed from '@/constants/watershed.json';

describe('Watershed report', () => {
    it('opens when point and button are selected', () => {
        cy.visit('/watershed')
        cy.intercept('/watershed/points')
    })
});
