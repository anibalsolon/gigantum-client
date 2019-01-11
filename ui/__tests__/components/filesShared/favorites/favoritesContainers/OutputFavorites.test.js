
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import OutputFavorites from 'Components/filesShared/favorites/favoritesContainers/OutputFavorites';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test OutputFavorites', () => {

        const wrapper = renderer.create(

           <OutputFavorites />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })