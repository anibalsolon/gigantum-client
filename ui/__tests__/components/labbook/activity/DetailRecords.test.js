
      import React from 'react';
      import renderer from 'react-test-renderer';
      import { mount } from 'enzyme';

      import DetailRecords from 'Components/labbook/activity/DetailRecords';

      import relayTestingUtils from '@gigantum/relay-testing-utils';
      import json from './__relaydata__/DetailRecords.json';

      test('Test DetailRecords', () => {
        const wrapper = renderer.create(

           relayTestingUtils.relayWrap(<DetailRecords />, {}, json.data.detailRecords),

        );

        const tree = wrapper.toJSON();

        expect(tree).toMatchSnapshot();
      });
