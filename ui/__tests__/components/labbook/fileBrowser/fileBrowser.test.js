import React from 'react';
import renderer from 'react-test-renderer';

import FileBrowser from 'Components/labbook/fileBrowser/FileBrowser';
import { mount, shallow } from 'enzyme';
import Auth from 'JS/Auth/Auth';
import history from 'JS/history';
import { BrowserRouter as Router } from 'react-router-dom';
import data from './../filesShared/__relayData__/MostRecentCode.json';
const auth = new Auth();

const variables = { first: 20, labbook: 'demo-lab-book' };
export default variables;

const { labbook } = data.data;
const fixtures = {
  clearSelectedFiles: jest.fn(),
  loadStatus: jest.fn(),
  selectedFiles: [],
  labbookId: labbook.id,
  sectionId: labbook.code.id,
  section: 'code',
  isLocked: false,
  ...labbook.code,
};

auth.isAuthenticated = function () { return true; };

describe('FileBrowser component', () => {
  it('Test FileBrowser Rendering', () => {
        const component = renderer.create(<FileBrowser
              {...fixtures}
            />);

        let tree = component.toJSON();
        expect(tree).toMatchSnapshot();
   });

   it('Test FileBrowser Rendering', () => {
     const localLabbooks = mount(<FileBrowser {...fixtures}/>);

     let tree = component.toJSON();
     expect(tree).toMatchSnapshot();
    });
});
