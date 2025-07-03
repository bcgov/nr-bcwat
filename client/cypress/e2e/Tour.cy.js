describe('tour', () => {
    it('starts and navigates through steps', () => {
        cy.visit('/watershed');
        cy.get('.help-icon').click();
        cy.get('.q-card.intro-popup').should('be.visible');
        cy.get('.q-btn.bg-primary > span > span').should('contain', 'Sure').click();
        // step 1:
        cy.get('.tour-text').should('contain', 'Markers show locations of existing water rights.');
        cy.get('[data-cy="tour-next"]').should('contain', 'next').click();
        // step 2:
        cy.get('.tour-text').should('contain', 'Markers show active and historical surface water quantity measurement locations.');
        cy.get('[data-cy="tour-next"]').click();
        // step 3:
        cy.get('.tour-text').should('contain', 'Waterbodies where surface water quality has been measured.');
        // step 4:
        cy.get('[data-cy="tour-next"]').click();
        cy.get('.tour-text').should('contain', 'Wells where ground water quality has been measured.');
        //step 3:
        cy.get('[data-cy="tour-back"]').click();
        cy.get('.tour-text').should('contain', 'Waterbodies where surface water quality has been measured.');
        // step 4:
        cy.get('[data-cy="tour-next"]').click();
        // step 5:
        cy.get('[data-cy="tour-next"]').click();
        // step 6:
        cy.get('[data-cy="tour-next"]').click();
        // step 7:
        cy.get('[data-cy="tour-next"]').click();
        // step 8:
        cy.get('[data-cy="tour-next"]').click();
        // step 9:
        cy.get('[data-cy="tour-next"]').click();
        // end:
        cy.get('[data-cy="tour-next"]').click();
    });
    it('starts and cancels', () => {
        cy.visit('/watershed');
        cy.get('.help-icon').click();
        cy.get('.q-card.intro-popup').should('be.visible');
        cy.get('.q-btn.bg-primary > span > span').should('contain', 'Sure').click();
        cy.get('.tour-text').should('contain', 'Markers show locations of existing water rights.')
        cy.get('[data-cy="tour-next"]').should('contain', 'next').click();
        cy.get('[data-cy="tour-leave"]').click();
        cy.get('.tour-container').should('not.exist');
    })
    it('Exit tour', () => {
        cy.visit('/watershed');
        cy.get('.help-icon').click();
        cy.get('.q-card.intro-popup').should('be.visible');
        cy.get('[data-cy="tour-cancel"]').should('contain', 'No Thanks').click();
        cy.get('.q-card.intro-popup').should('not.exist');
    })
});
