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
    selectedBranchname: null,
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
  /**
    @param {String} selectedBranchname
    sets selected branch in state
    @return {}
  */
  _selectBranchname(selectedBranchname) {
    if (this.state.selectedBranchname === selectedBranchname) {
      this.setState({ selectedBranchname: null });
    } else {
      this.setState({ selectedBranchname });
    }
  }
  /**
    renders JSX for actions section
    @return {JSX}
  */
  _renderActions() {
    return (
      <div className="Branches__actions-section">
      <button
        className="Branches__btn Branches__btn--reset"
        onClick={() => console.log('button') }
      />
      <button
        className="Branches__btn Branches__btn--switch"
        onClick={() => console.log('button') }
      />
      <button
        className="Branches__btn Branches__btn--merge"
        onClick={() => console.log('button') }
      />
      <button
        className="Branches__btn Branches__btn--delete"
        onClick={() => console.log('button') }
      />
      <button
        className="Branches__btn Branches__btn--sync"
        onClick={() => console.log('button') }
      />
    </div>)
  }

  render() {
    const { props, state } = this,
          currentBranchNameCSS = classNames({
            'Branches__current-branchname': true,
            // TODO change based on commits ahead & behind
            'Branches__current-branchname--changed': false,
          });
    console.log(props)

    const filteredBranches = props.branches.filter(branch => branch.branchName !== props.activeBranch.branchName);
    return (
      <div>
      { props.sidePanelVisible
        && <SidePanel
            toggleSidePanel={props.toggleSidePanel}
            isSticky={props.isSticky}
            renderContent={() => <div className="Branches">
                <div className="Branches__header">
                  <div className="Branches__title">Manage Branches</div>
                  <button
                    className="Branches__btn Branches__btn--create"
                    onClick={() => this.props.toggleModal('createBranchVisible') }
                  />
                </div>

              <div className="Branches__branch--current">
                <div className="Branches__base-section">
                  <div className="Branches__label">Current Branch:</div>
                  <div className="Branches__branchname-container">
                    <div className="Branches__branchname">{props.activeBranch.branchName}</div>
                    <div className="Branches__status" />
                  </div>
                </div>
                {
                  this._renderActions()
                }
              </div>

              {
                filteredBranches.map((branch) => {
                  const y = 'test';
                  return (
                    <div
                      key={branch.branchName}
                      className="Branches__branch"
                      onClick={() => this._selectBranchname(branch.branchName)}
                    >
                      <div className="Branches__base-section">
                        <div className="Branches__branchname-container">
                          <div className="Branches__branchname">{branch.branchName}</div>
                          <div className="Branches__status" />
                        </div>
                      </div>
                      {
                        state.selectedBranchname === branch.branchName &&
                        this._renderActions()
                      }
                    </div>
                  )
                })
              }

            </div>
          }
           />
      }
      </div>
    );
  }
}

export default Branches;
