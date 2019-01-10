// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
import uuidv4 from 'uuid/v4';
// assets
import './DatasetActionsMenu.scss';
// store
import store from 'JS/redux/store';
import { setMultiInfoMessage } from 'JS/redux/reducers/footer';

export default class DatasetActionsMenu extends Component {
  constructor(props) {
  	super(props);
  	this._closePopup = this._closePopup.bind(this);
    this._setWrapperRef = this._setWrapperRef.bind(this);
  }

  state = {
    popupVisible: false,
  }
  /**
  *  LIFECYCLE MEHTODS START
  */
  componentDidMount() {
    window.addEventListener('click', this._closePopup);
  }

  componentWillMount() {
    window.removeEventListener('click', this._closePopup);
  }
  /**
  *  LIFECYCLE MEHTODS END
  */

  /**
  *  @param {Object} event
  *  closes popup when clicking
  *  @return {}
  */
  _closePopup(evt) {
    if (this.state.popupVisible && this[this.props.edge.node.id] && !this[this.props.edge.node.id].contains(evt.target)) {
      this.setState({ popupVisible: false });
    }
  }

  /**
  *  @param {Obect} evt
  *  @param {boolean} popupVisible - boolean value for hiding and showing popup state
  *  triggers favoirte unfavorite mutation
  *  @return {}
  */
  _togglePopup(evt, popupVisible) {
    if (!popupVisible) {
      evt.stopPropagation(); // only stop propagation when closing popup, other menus won't close on click if propagation is stopped
    }
    this.setState({ popupVisible });
  }

  /**
  *  @param {event} evt - event from clicking delete button
  *  triggers DeleteLabbookFileMutation
  *  @return {}
  */
  _triggerDeleteMutation(evt) {
    const deleteFileData = {
      filePaths: [this.props.edge.node.key],
      edges: [this.props.edge],
    };

    this.props.mutations.deleteLabbookFiles(deleteFileData, (reponse) => {});

    this._togglePopup(evt, false);
  }

  /**
  *  @param {Object} node - Dom object to be assigned as a ref
  *  set wrapper ref
  *  @return {}
  */
   _setWrapperRef(node) {
     this[this.props.edge.node.id] = node;
   }

   /**
   *  @param {} node - Dom object to be assigned as a ref
   *  set wrapper ref
   *  @return {}
   */
   _downloadFile(isLocal) {
     if (!isLocal) {
      const id = uuidv4;
      this.setState({ fileDownloading: true });
      const searchChildren = (parent) => {
        if (parent.children) {
          Object.keys(parent.children).forEach((childKey) => {
            if (parent.children[childKey].edge) {
              if (!parent.children[childKey].edge.node.isDir) {
                let key = parent.children[childKey].edge.node.key;
                let splitKey = key.split('/');
                key = splitKey.slice(1, splitKey.length).join('/');
                keyArr.push(key);
              }
              searchChildren(parent.children[childKey]);
            }
          });
        }
      };

      let { key, owner, datasetName } = this.props.edge.node;
      const labbookOwner = store.getState().routes.owner;
      const labbookName = store.getState().routes.labbookName;
      let splitKey = key.split('/');

      if (this.props.section === 'data') {
        owner = labbookOwner;
        datasetName = labbookName;
      }

      key = splitKey.slice(1, splitKey.length).join('/');
      const keyArr = this.props.edge.node.isDir ? [] : [key];
      if (this.props.folder && !this.props.isParent) {
        searchChildren(this.props.fullEdge);
      }
      let data;

      if (this.props.section === 'data') {
        data = {
          owner,
          datasetName,
        };
      } else {
        data = {
          owner,
          datasetName,
          labbookName,
          labbookOwner,
        };
      }
      if (this.props.isParent) {
        data.allKeys = true;
      } else {
        data.allKeys = false;
        data.keys = keyArr;
      }

      const callback = (response, error) => {
        if (error) {
          this.setState({ fileDownloading: false });
        } else {
          this.setState({ fileDownloading: false });
        }
      };


      this.props.mutations.downloadDatasetFiles(data, callback);
     }
   }

  render() {
    let isLocal = true;
    const searchChildren = (parent) => {
      if (parent.children) {
        Object.keys(parent.children).forEach((childKey) => {
          if (parent.children[childKey].edge) {
            if (parent.children[childKey].edge.node.isLocal === false) {
              isLocal = false;
            }
            searchChildren(parent.children[childKey]);
          }
        });
      }
    };
    if (this.props.fullEdge) {
      searchChildren(this.props.fullEdge);
    } else {
      isLocal = this.props.edge.node.isLocal;
    }

    const manageCSS = classNames({
            DatasetActionsMenu__item: true,
            'DatasetActionsMenu__item--manage': true,
          }),
          popupCSS = classNames({
            DatasetActionsMenu__popup: true,
            hidden: !this.state.popupVisible,
            ToolTip__message: true,
          }),
          removeCSS = classNames({
            'DatasetActionsMenu__item DatasetActionsMenu__item--remove': true,
          }),
          downloadCSS = classNames({
            DatasetActionsMenu__item: true,
            'DatasetActionsMenu__item--download': (!this.props.edge.node.isLocal && !isLocal) && this.props.section !== 'data' && !this.state.fileDownloading,
            'DatasetActionsMenu__item--downloaded': (this.props.edge.node.isLocal || isLocal) && this.props.section !== 'data' && !this.state.fileDownloading,
            'DatasetActionsMenu__item--download-grey': (!this.props.edge.node.isLocal && !isLocal) && this.props.section === 'data' && !this.state.fileDownloading,
            'DatasetActionsMenu__item--downloaded-grey': (this.props.edge.node.isLocal || isLocal) && this.props.section === 'data' && !this.state.fileDownloading,
            'DatasetActionsMenu__item--loading': this.state.fileDownloading,
          }),
          downloadText = isLocal ? 'Downloaded' : this.props.isParent ? 'Download All' : this.props.folder ? 'Download Directory' : 'Download';


    return (

        <div
          className="DatasetActionsMenu"
          key={`${this.props.edge.node.id}-action-menu}`}
          ref={this._setWrapperRef}>

          { this.props.edge.node.isDatasetRoot &&
            <div className="DatasetActionsMenu__database-actions">
              <div
                  onClick={() => { this._updateItems(true); }}
                  className="DatasetActionsMenu__item DatasetActionsMenu__item--details"
                  name="Details">
                  Details
              </div>
              <div
                onClick={ () => { this._remove(); }}
                className={removeCSS}
                name="Remove">
              </div>

              <div
                onClick={ () => { this._manageDatasets(); }}
                className={manageCSS}
                name="Manage">
              </div>
            </div>
          }

          <div
            onClick={() => this._downloadFile(this.props.edge.node.isLocal || isLocal)}
            className={downloadCSS}
            name={downloadText}>
          </div>
        </div>
    );
  }
}
