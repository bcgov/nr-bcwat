import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import ChartLegend from '@/components/streamflow/ChartLegend.vue';

const legendContents = [
  {
    label: 'Test Label 1',
    color: 'red',
  },
  {
    label: 'Test Label 2',
    color: 'white',
  },
];


describe('ChartLegend.vue', () => {
  const div = document.createElement('div')
  div.id = 'root'
  document.body.appendChild(div)

  it('renders the correct message', async () => {
    const wrapper = mount(ChartLegend, {
      props: {
        legendList: legendContents,
      },
      attachTo: '#root'
    });
    const chartLegendEls = wrapper.findAll('[data-test="legend-label"]')
    legendContents.forEach((el, idx) => {
      expect(chartLegendEls[idx].text()).toContain(el.label);
    })
  });

  it('renders the correct color', () => {
    const wrapper = mount(ChartLegend, {
      props: {
        legendList: legendContents,
      },
      attachTo: '#root'
    });
    const chartLegendEls = wrapper.findAll('[data-test="legend-color"]')
    legendContents.forEach((el, idx) => {
      expect(chartLegendEls[idx].html()).toContain(el.color);
    })
  });
});
