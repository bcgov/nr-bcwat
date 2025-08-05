import ClimateChart from "@/components/watershed/report/ClimateChart.vue";
import watershedReport from '../../../fixtures/watershedReport.json';

const temperatureChartData = watershedReport.climateChartData.temperature;
const temperatureId = 'temperature';

describe('<ClimateChart />', () => {
    it('mounts and renders temperature chart', () => {
        cy.mount(ClimateChart, {
            props: {
                chartData: temperatureChartData,
                chartId: temperatureId,
                areaColor: 'red',
                lineColor: 'black',
            }
        });
        cy.get(`#climate-${temperatureId}-chart > svg > g > .${temperatureId}-projected`).should('exist').and('be.visible');
        cy.get(`#climate-${temperatureId}-chart > svg > g > .${temperatureId}-projected`).should('have.css', 'fill').and('eq', 'rgb(255, 0, 0)');
        cy.get(`#climate-${temperatureId}-chart > svg > g > .text-capitalize`).should('contain', '°C');
    });
    it('mounts and renders non-temperature chart', () => {
        cy.mount(ClimateChart, {
            props: {
                chartData: temperatureChartData,
                chartId: 'test',
                areaColor: 'red',
                lineColor: 'black',
            }
        });
        cy.get('#climate-test-chart > svg > g > .test-projected').should('exist').and('be.visible');
        cy.get('#climate-test-chart > svg > g > .test-projected').should('have.css', 'fill').and('eq', 'rgb(255, 0, 0)');
        cy.get('#climate-test-chart > svg > g > .text-capitalize').should('contain', 'mm');
    });
});
