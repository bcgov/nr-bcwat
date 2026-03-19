import MapPointSelector from '@/components/MapPointSelector.vue';

describe('<MapPointSelector />', () => {
    it('watershed page', () => {
        cy.mount(MapPointSelector, {
            props: {
                points: [{
                    properties: {
                        lic: "TEST LICENSE",
                        org: "DOMESTIC",
                        qty: 10000,
                        src_name: "TEST SOURCE",
                        pod: "TEST POD",
                    }
                }],
                open: true,
                page: 'watershed',
            }
        });
        cy.get('[data-cy="point-qty"]').should('have.text', ' Quantity: 10000 m³/year ')
    });

    it('waterportal page', () => {
        cy.mount(MapPointSelector, {
            props: {
                points: [{
                    properties: {
                        name: "TEST NAME",
                        yr: "[2010,2011]",
                        area: 1000,
                        net: "TEST NETWORK",
                    }
                }],
                open: true,
                page: 'waterportal',
            }
        });

        cy.get('[data-cy="point-yr"]').should('have.text', ' Year Range: 2010-2011')
        cy.get('[data-cy="point-area"]').should('have.text', ' Area: 1000.0km2')
    });
});
