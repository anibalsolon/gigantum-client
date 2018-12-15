// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
import uuidv4 from 'uuid/v4';
// components
import ToolTip from 'Components/shared/ToolTip';
import Modal from 'Components/shared/Modal';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
// store
import store from 'JS/redux/store';
// assets
import './ImportModule.scss';
// mutations
import ImportRemoteDatasetMutation from 'Mutations/ImportRemoteDatasetMutation';

export default class ImportModule extends Component {
  constructor(props) {
    super(props);

    this.state = {
      show: false,
      remoteURL: '',
      files: [],
    };
    this._importingState = this._importingState.bind(this);
    this._clearState = this._clearState.bind(this);
  }

  /**
  *  @param {}
  *  clears state of file and sets css back to import
  *  @return {}
  */
  _clearState = () => {
    this.setState({ files: [], isImporting: false, readyDataset: null });
  }

  /**
  *  @param {}
  *  sets state of app for importing
  *  @return {}
  */
  _importingState = () => {
    this.setState({ isImporting: true });
  }
  /**
  *  @param {}
  *  closes import modal
  *  @return {}
  */
  _closeImportModal = () => {
    this.setState({ showImportModal: false, remoteUrl: '', readyDataset: null });
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
  /**
  *  @param {Object} evt
  *  imports dataset from remote url, builds the image, and redirects to imported dataset
  *  @return {}
  */
  importDataset = (evt) => {
    const id = uuidv4(),
      datasetName = this.state.remoteURL.split('/')[this.state.remoteURL.split('/').length - 1],
      owner = this.state.remoteURL.split('/')[this.state.remoteURL.split('/').length - 2],
      remote = `https://repo.gigantum.io/${owner}/${datasetName}.git`;
    const self = this;

    UserIdentity.getUserIdentity().then((response) => {
      if (navigator.onLine) {
        if (response.data) {
          if (response.data.userIdentity.isSessionValid) {
            self._importingState();

            store.dispatch({
              type: 'MULTIPART_INFO_MESSAGE',
              payload: {
                id,
                message: 'Importing Dataset please wait',
                isLast: false,
                error: false,
              },
            });

            self._importRemoteDataset(owner, datasetName, remote, id);
          } else {
            this.props.auth.renewToken(true, () => {
              this.setState({ showLoginPrompt: true });
            }, () => {
              this.importDataset();
            });
          }
        }
      } else {
        this.setState({ showLoginPrompt: true });
      }
    });
  }

  /**
  *  @param {String, String, String, String}
  *  trigers ImportRemoteDatasetMutation
  *  @return {}
  */
  _importRemoteDataset(owner, datasetName, remote, id) {
    const self = this;

    ImportRemoteDatasetMutation(owner, datasetName, remote, (response, error) => {
      this._clearState();
      if (error) {
        console.error(error);
        store.dispatch({
          type: 'MULTIPART_INFO_MESSAGE',
          payload: {
            id,
            message: 'ERROR: Could not import remote Dataset',
            messageBody: error,
            error: true,
          },
        });
      } else if (response) {
        store.dispatch({
          type: 'MULTIPART_INFO_MESSAGE',
          payload: {
            id,
            message: `Successfully imported remote Dataset ${datasetName}`,
            isLast: true,
            error: false,
          },
        });
        self.props.history.replace(`/datasets/${response.importRemoteDataset.newDatasetEdge.node.owner}/${datasetName}`);
      }
    });
  }

  /**
  *  @param {Object} evt
  *  updated url in state
  *  @return {}
  */
  _updateRemoteUrl(evt) {
    const newValue = evt.target.value;
    const datasetName = newValue.split('/')[newValue.split('/').length - 1];
    const owner = newValue.split('/')[newValue.split('/').length - 2];
    if (newValue.indexOf('gigantum.com/') > -1 && datasetName && owner) {
      this.setState({
        readyDataset: {
          datasetName,
          owner,
        },
      });
    }
    this.setState({ remoteURL: evt.target.value });
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
    {
      self.state.showImportModal &&
      <Modal
        header="Import Dataset"
        handleClose={() => self._closeImportModal()}
        size="large"
        renderContent={() =>
          (<Fragment>
            <div className="ImportModal">
              <p>In order to import a dataset by either pasting a URL or drag & dropping below</p>
              <input
                className="Import__input"
                type="text"
                placeholder="Paste Dataset URL"
                onChange={evt => self._updateRemoteUrl(evt)}
                defaultValue={self.state.remoteUrl}
              />

              <div className="ImportDropzone">
                {
                  self.state.readyDataset ?
                  <div className="Import__ReadyDataset">
                    <div>Select Import to import the following dataset</div>
                    <hr/>
                    <div>Dataset Owner: {self.state.readyDataset.owner}</div>
                    <div>Dataset Name: {self.state.readyDataset.datasetName}</div>
                  </div> :
                  <div className= "DropZone" >
                    Drag and drop the exported Dataset here
                  </div>
                }
              </div>
              <div className="Import__buttonContainer">
                <button
                  onClick={() => { self.importDataset(); }}
                  disabled={!self.state.readyDataset}
                >
                  Import
                </button>
                <button onClick={() => self._closeImportModal()}>Cancel</button>
              </div>
            </div>
            </Fragment>)
        }
      />
    }

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

    <div
      className="btn--import"
      onClick={(evt) => {
        self.setState({ showImportModal: true });
      }}
    >
      Import Existing
    </div>

    <ToolTip section="createLabbook" />


  </div>);
};

