
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import CodeFavorites from 'Components/filesShared/favorites/favoritesContainers/CodeFavorites';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test CodeFavorites', () => {

        const wrapper = renderer.create(

           <CodeFavorites />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })