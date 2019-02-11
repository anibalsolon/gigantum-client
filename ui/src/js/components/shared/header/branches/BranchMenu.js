// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// componenets
import Loader from 'Components/common/Loader';
import BranchCard from './BranchCard';
// assets
import './BranchMenu.scss';

class BranchMenu extends Component {
  constructor(props) {
  	super(props);

  	this.state = {
      switchMenuVisible: false,
    };
  }

  /**
    @param {} -
    sets state to toggle the switch dropdown
    @return {}
  */
  _toggleBranchSwitch() {
     const { state } = this;
     this.setState({ switchMenuVisible: !state.switchMenuVisible });
  }

  render() {
    const { props, state } = this,
          switchDropdownCSS = classNames({
            'BranchMenu__dropdown-menu': true,
            hidden: !state.switchMenuVisible,
          });
    return (
      <div className="BranchMenu">
          <div className="BranchMenu__dropdown">
                <div
                onClick={() => this._toggleBranchSwitch() }
                className="BranchMenu__dropdown-btn">
                  master
                </div>
                <div className={switchDropdownCSS}></div>
          </div>
          <div className="BranchMenu__buttons">
            <button
              className="BranchMenu__btn BranchMenu__btn--manage Btn--flat"
              type="Submit">
              Manage
            </button>
            <button
              className="BranchMenu__btn BranchMenu__btn--manage Btn--flat"
              type="Submit">
              Create
            </button>
            <button
              className="BranchMenu__btn BranchMenu__btn--manage Btn--flat"
              type="Submit">
              Sync
            </button>
          </div>
      </div>
    );
  }
}


export default BranchMenu;
