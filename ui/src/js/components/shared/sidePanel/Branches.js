// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
import { Link } from 'react-router-dom';
import { boundMethod } from 'autobind-decorator';
import shallowCompare from 'react-addons-shallow-compare';
// config
import Config from 'JS/config';
// store
import store from 'JS/redux/store';
import {
  setSyncingState,
  setPublishingState,
  setExportingState,
  setModalVisible,
  setUpdateDetailView,
} from 'JS/redux/reducers/labbook/labbook';
// components
import ToolTip from 'Components/common/ToolTip';
import SidePanel from './SidePanel';
// assets
import './Branches.scss';

class Branches extends Component {
  state = {
    sidePanelVisible: this.props.sidePanelVisible,
  }

  static getDerivedStateFromProps(nextProps, state) {
     return ({
       sidePanelVisible: nextProps.sidePanelVisible,
       ...state,
     });
  }

  shouldComponentUpdate(nextProps, nextState) {
    return shallowCompare(this, nextProps, nextState);
  }

  render() {
    const { props, state } = this;

    return (
      <div>
      { props.sidePanelVisible
        && <SidePanel
            toggleSidePanel={props.toggleSidePanel}
            isSticky={props.isSticky}
            renderContent={() => <div className="Branches"></div> }
           />
      }
      </div>
    );
  }
}

export default Branches;
