import React from 'react';
import PackageCount from 'Components/labbook/overview/PackageCount';
import { shallow, mount } from 'enzyme';
import renderer from 'react-test-renderer';
import { MemoryRouter } from 'react-router-dom';
import config from '../config';

let _setBuildingState = ((state) => {

});

describe('Test PackageCount rendering', () => {
  it('renders snapshot', async () => {
    const component = await renderer.create(

        <PackageCount labbookName={config.data.labbook.name} />,

    );
    let tree = component.toJSON();
    expect(component).toMatchSnapshot();
  });
});
