import { addCommas } from '@/utils/stringHelpers.js';
import { expect } from 'vitest';

const testVals = [
    123123123123,
    -1,
    1234.1234
]

describe('Adding comma helper', () => {
    it('converts number to string correctly', () => {
        // numbers under 1000 are not converted
        expect(addCommas(testVals[0])).toEqual('123,123,123,123');
        expect(addCommas(testVals[1])).toEqual('-1');
        expect(addCommas(testVals[2])).toEqual('1,234.1234');
    })
});
