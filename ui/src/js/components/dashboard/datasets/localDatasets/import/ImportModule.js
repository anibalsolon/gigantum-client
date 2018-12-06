// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
// components
import ToolTip from 'Components/shared/ToolTip';
// store
import store from 'JS/redux/store';
// assets
import './ImportModule.scss';

export default class ImportModule extends Component {
  constructor(props) {
    super(props);

    this.state = {
      show: false,
    };
  }

  /**
  *  @param {}
  *  shows create project modal
  *  @return {}
  */
  _showModal(evt) {
    if (navigator.onLine) {
      if (evt.target.id !== 'file__input-label') {
        this.props.showModal();
      }
    } else {
      store.dispatch({
        type: 'ERROR_MESSAGE',
        payload: {
          message: 'Cannot create a Project at this time.',
          messageBody: [
            {
              message: 'An internet connection is required to create a Project.',
            },
          ],
        },
      });
    }
  }

  render() {
    const loadingMaskCSS = classNames({
      'ImportModule__loading-mask': this.state.isImporting,
      hidden: !this.state.isImporting,
    });

    return (<Fragment>

      <div id="dropZone" className="ImportModule Card Card--line-50 Card--text-center Card--add Card--import column-4-span-3" key="addLabbook" ref={div => this.dropZone = div} type="file" onDragEnd={evt => this._dragendHandler(evt)} onDrop={evt => this._dropHandler(evt)} onDragOver={evt => this._dragoverHandler(evt)}>
        <ImportMain self={this} />
        <div className={loadingMaskCSS} />
      </div>

    </Fragment>);
  }
}

const ImportMain = ({ self }) => {
  const importCSS = classNames({
    'btn--import': true,
    'btn--expand': self.state.importTransition,
    'btn--collapse': !self.state.importTransition && self.state.importTransition !== null,
  });

  return (<div className="Import__dataset-main">

    <div className="Import__dataset-header">
      <div className="Import__dataset-icon">
        <div className="Import__dataset-add-icon" />
      </div>
      <div className="Import__dataset-title">
        <h4>Add Dataset</h4>
      </div>

    </div>

    <div
      className="btn--import"
      onClick={(evt) => {
        self._showModal(evt);
      }}
    >
      Create New
    </div>

    <ToolTip section="createLabbook" />


  </div>);
};

