// vendor
import React, { Component, Fragment } from 'react';
// utils
import ContainerMutations from './utils/ContainerMutations';
// component
import ContainerStatus from './containerStatus/ContainerStatus';
import DevTools from './devTools/DevTools';
// assets
import './Container.scss';

class Container extends Component {
  state = {
    containerMutations: new ContainerMutations({ name: this.props.labbook.name, owner: this.props.labbook.owner }),
  }

  render() {
    const { props, state } = this,
          { labbook } = props;
    return (
        <div className="Container">

            <DevTools
              {...props}
              containerMutations={state.containerMutations}
              isBuilding={state.isBuilding}
            />

            <ContainerStatus
              {...props}
              containerMutations={state.containerMutations}
              base={labbook.environment.base}
              isBuilding={state.isBuilding}
            />

        </div>
    );
  }
}

export default Container;
