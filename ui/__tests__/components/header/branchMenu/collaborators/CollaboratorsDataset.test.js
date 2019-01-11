
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import CollaboratorsDataset from 'Components/header/branchMenu/collaborators/CollaboratorsDataset';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test CollaboratorsDataset', () => {

        const wrapper = renderer.create(

           <CollaboratorsDataset />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })