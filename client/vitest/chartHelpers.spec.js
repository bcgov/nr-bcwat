import { sciNotationConverter } from '@/utils/chartHelpers.js';
import { expect } from 'vitest';

const testVals = [
    -10000,
    -1,
    0,
    1,
    999,
    1000,
    1000000000000 // 12 0s
]

describe('Scientific Notation Converter', () => {
    it('converts correctly', () => {
        // numbers under 1000 are not converted
        expect(sciNotationConverter(testVals[0])).toEqual(testVals[0])
        expect(sciNotationConverter(testVals[1])).toEqual(testVals[1])
        expect(sciNotationConverter(testVals[2])).toEqual(testVals[2])
        expect(sciNotationConverter(testVals[3])).toEqual(testVals[3])
        expect(sciNotationConverter(testVals[4])).toEqual(testVals[4])
        expect(sciNotationConverter(testVals[5])).toEqual('1×10³')
        expect(sciNotationConverter(testVals[6])).toEqual('1×10¹²')
    })
});
