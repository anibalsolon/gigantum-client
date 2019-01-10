
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import InputFavorites from 'Components/filesShared/favorites/favoritesContainers/InputFavorites';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test InputFavorites', () => {

        const wrapper = renderer.create(

           <InputFavorites />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })