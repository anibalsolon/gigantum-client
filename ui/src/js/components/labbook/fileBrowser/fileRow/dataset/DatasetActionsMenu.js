// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// assets
import './DatasetActionsMenu.scss';

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
   _downloadFile() {
     console.log(this.props);
   }
   /**
   *  @param {} node - Dom object to be assigned as a ref
   *  set wrapper ref
   *  @return {}
   */
   _manageDatasets() {
    console.log(this.props);
   }
  render() {

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
            'DatasetActionsMenu__item--download': !this.props.edge.node.isDownloaded,
            'DatasetActionsMenu__item--downloaded': this.props.edge.node.isDownloaded,
          });

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
            onClick={() => this._downloadFile()}
            className={downloadCSS}
            name="Download">
          </div>
        </div>
    );
  }
}
