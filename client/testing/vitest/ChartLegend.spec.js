import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import ChartLegend from '@/components/streamflow/ChartLegend.vue';

const legendContents = [
  {
    label: 'Test Label 1',
    color: 'black',
  },
  {
    label: 'Test Label 2',
    color: 'white',
  },
];

describe('ChartLegend.vue', () => {
  it('renders the correct message', () => {
    const wrapper = mount(ChartLegend, {
      props: {
        legendList: legendContents
      }
    });
    console.log(wrapper)
  });

  // it('renders the correct message', () => {
  //   const wrapper = mount(ChartLegend);
  //   console.log(wrapper)
  //   // expect(wrapper.text()).toContain('Hello, Vue!');
  // });
});
