// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
import { boundMethod } from 'autobind-decorator';
// store
import store from 'JS/redux/store';
import { setContainerState } from 'JS/redux/reducers/labbook/overview/overview';
import { setContainerStatus, setContainerMenuVisibility } from 'JS/redux/reducers/labbook/containerStatus';
import { setContainerMenuWarningMessage, setCloseEnvironmentMenus } from 'JS/redux/reducers/labbook/environment/environment';
import { setPackageMenuVisible } from 'JS/redux/reducers/labbook/environment/packageDependencies';
import { setBuildingState, setMergeMode } from 'JS/redux/reducers/labbook/labbook';
import { setErrorMessage, setInfoMessage, setWarningMessage } from 'JS/redux/reducers/footer';
// assets
import './DevTools.scss';

class DevTools extends Component {

  state = {
    isMouseOver: false,
    selectedDevTool: 'jupyterLab',
    showDevList: false,
  }

  /**
  *  @param {string} developmentTool
  *  @param {string} developmentTool
  *  mutation to trigger opening of development tool
  *  @return {}
  */
  @boundMethod
  _openDevToolMuation(developmentTool) {
    const { props, state } = this,
          { containerStatus, imageStatus } = props,
          { owner, name } = props.labbook,
          tabName = `${developmentTool}-${owner}-${name}`;

    const labbookCreationDate = Date.parse(`${this.props.creationDateUtc}Z`);
    const timeNow = Date.parse(new Date());

    const timeDifferenceMS = timeNow - labbookCreationDate;

    let status = (containerStatus === 'RUNNING') ? 'Running' : containerStatus;
    status = (containerStatus === 'NOT_RUNNING') ? 'Stopped' : status;
    status = (imageStatus === 'BUILD_IN_PROGRESS') ? 'Building' : status;
    status = (imageStatus === 'BUILD_FAILED') ? 'Rebuild' : status;
    status = (imageStatus === 'DOES_NOT_EXIST') ? 'Rebuild' : status;
    status = ((imageStatus === 'DOES_NOT_EXIST') || (imageStatus === 'BUILD_IN_PROGRESS')) && (timeDifferenceMS < 15000) ? 'Building' : status;

    if (status !== 'Stopped' && status !== 'Running') {
      setWarningMessage('Could not launch development environment as the project is not ready.');
    } else if (status === 'Stopped') {
      this.props.setInfoMessage('Starting Project container. When done working, click Stop to shutdown the container.');
      this.setState({
        status: 'Starting',
        contanerMenuRunning: false,
      });
      setMergeMode(false, false);

      this._startContainerMutation(true);

    } else if (window[tabName] && !window[tabName].closed) {
      window[tabName].focus();
    } else {
      setInfoMessage(`Starting ${developmentTool}, make sure to allow popups.`);
      const data = { devTool: developmentTool };
      props.containerMutations.startDevTool(
        data,
        (response, error) => {
          if (response.startDevTool) {
            const tabName = `${developmentTool}-${owner}-${name}`;
            let path = `${window.location.protocol}//${window.location.hostname}${response.startDevTool.path}`;
            if (developmentTool === 'Notebook') {
              if (path.includes('/lab/tree')) {
                path = path.replace('/lab/tree', '/tree');
              } else {
                path = `${path}/tree/code`;
              }
            }

            window[tabName] = window.open(path, tabName);
          }

          if (error) {
            setErrorMessage('Error Starting Dev tool', error);
          }
        },
      );
    }
  }

  render() {
    const { props, state } = this,
          devTools = props.labbook.environment.base.developmentTools,
          jupyterButtonCss = classNames({
            'DevTools-button': true,
            'ContainerStatus__button--bottom': state.isMouseOver,
          }),
          containerMenuCSS = classNames({
            'DevTools-menu': true,
            hidden: !state.showDevList,
            'DevTools-menu--hover': state.isMouseOver,
          }),
          expandToolsCSS = classNames({
            'ContainerStatus__expand-tools': true,
            'ContainerStatus__expand-tools--open': state.showDevList,
          }),
          containerMenuIconCSS = classNames({
            'DevTools-menu-arrow': true,
            hidden: !state.pluginsMenu,
          }),
          containerSelectCSS = classNames({
            'ContainerStatus__selected-tool': true,
            'ContainerStatus__selected-tool--long': devTools.length === 0,
          });

    return (
        <div className="DevTools">
          <div className={jupyterButtonCss}>
            <div
              className={containerSelectCSS}
              onClick={() => { this._openDevToolMuation(state.selectedDevTool); }}>
                {state.selectedDevTool}
            </div>
            {
              devTools.length !== 0 &&
              <div
                className={expandToolsCSS}
                onClick={() => this.setState({ showDevList: !state.showDevList })}>
              </div>
            }
          </div>

          <div className={containerMenuIconCSS} />

          <ul className={containerMenuCSS}>
            {

              devTools.map(developmentTool => (

                <li
                  key={developmentTool}
                  className="DevTools-list-item jupyter-icon"
                  onClick={() => {
                    this.setState({ selectedDevTool: developmentTool, showDevList: false });
                    this._openDevToolMuation(developmentTool);
                  }}>
                  {developmentTool}
                </li>
                ))
            }
          </ul>
        </div>
    );
  }
}

export default DevTools;
