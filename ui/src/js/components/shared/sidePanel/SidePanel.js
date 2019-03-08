// vendor
import React, { Component, Fragment } from 'react';
import ReactDom from 'react-dom';
import classNames from 'classnames';
import { Link } from 'react-router-dom';
import { boundMethod } from 'autobind-decorator';
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
import Tooltip from 'Components/common/Tooltip';
// assets
import './SidePanel.scss';

class SidePanel extends Component {
  state = {
    isPanelOpen: false,
  }
  /**
    @param {} -
    updates panelState
    @return {}
  */
  @boundMethod
  _togglePanel() {
    const { state } = this;
    this.setState({ isPanelOpen: !state.isPanelOpen });
  }

  render() {
    const { props, state } = this,
           sidePanelCSS = classNames({
             SidePanel: true,
             'SidePanel--sticky': props.isSticky && !props.isDeprecated,
             'SidePanel--is-deprecated': props.isDeprecated && !props.isSticky,
             'SidePanel--is-deprecated-sticky': props.isDeprecated && props.isSticky,
           });
    return (
      ReactDom.createPortal(
        <div className={sidePanelCSS}>
            <div className="SidePanel__header">
              <div
              onClick={() => props.toggleSidePanel(false)}
              className="SidePanel__btn SidePanel__btn--close" />
            </div>
            <div className="SidePanel__body">
              { props.renderContent() }
            </div>
        </div>, document.getElementById('side_panel'),
      )
    );
  }
}

export default SidePanel;
