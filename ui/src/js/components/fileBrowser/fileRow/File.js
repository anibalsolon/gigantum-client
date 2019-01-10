// vendor
import React, { Component } from 'react';
import Moment from 'moment';
import fileIconsJs from 'file-icons-js';
import classNames from 'classnames';
import { DragSource, DropTarget } from 'react-dnd';
import { NativeTypes } from 'react-dnd-html5-backend';
import TextTruncate from 'react-text-truncate';
// components
import Connectors from './../utilities/Connectors';
import ActionsMenu from './ActionsMenu';
import DatasetActionsMenu from './dataset/DatasetActionsMenu';
// config
import config from 'JS/config';
// assets
import './File.scss';

class File extends Component {
  constructor(props) {
      super(props);
      this.state = {
          isDragging: props.isDragging,
          isSelected: (props.isSelected || this.props.childrenState[this.props.fileData.edge.node.key].isSelected) || false,
          stateSwitch: false,
          newFileName: props.filename,
          renameEditMode: false,
          hover: false,
      };
      this._setSelected = this._setSelected.bind(this);
      this._renameEditMode = this._renameEditMode.bind(this);
      this._triggerMutation = this._triggerMutation.bind(this);
      this._clearState = this._clearState.bind(this);
      this._setHoverState = this._setHoverState.bind(this);
      this._checkHover = this._checkHover.bind(this);
  }

  static getDerivedStateFromProps(nextProps, state) {
    let isSelected = (nextProps.multiSelect === 'all')
      ? true
      : (nextProps.multiSelect === 'none')
      ? false
      : state.isSelected;

      if ((nextProps.isOverCurrent !== nextProps.isOverChildFile) && !nextProps.isDragging && state.hover) {
        nextProps.updateParentDropZone(nextProps.isOverCurrent);
      }
    return {
      ...state,
      isSelected,
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.state.renameEditMode) {
           this.reanmeInput.focus();
      }
  }

  /**
  *  @param {boolean} isSelected - sets if file has been selected
  *  sets elements to be selected and parent
  */
  _setSelected(isSelected) {
      this.props.updateChildState(this.props.fileData.edge.node.key, isSelected, false);
      this.setState({ isSelected }, () => {
          Object.keys(this.refs).forEach((ref) => {
              this.refs[ref].getDecoratedComponentInstance().getDecoratedComponentInstance()._setSelected();
          });
          if (this.props.checkParent) {
              this.props.checkParent();
          }
      });
  }
    /**
    *  @param {}
    *  sets dragging state
    */
   _mouseEnter() {
    if (this.props.setParentDragFalse) {
      this.props.setParentDragFalse();
    }

    if (this.state.isDragging && this.state.isHovered) {
      this.setState({ isDragging: true, isHovered: true });
    }
  }
  /**
  *  @param {}
  *  sets dragging state
  */
  _mouseLeave() {
    if (this.props.setParentDragTrue) {
      this.props.setParentDragTrue();
    }
    if (!this.state.isDragging && !this.state.isHovered) {
      this.setState({ isDragging: false, isHovered: false });
    }
  }
  /**
  *  @param {}
  *  sets dragging state to true
  */
  _checkHover() {
    if (this.state.isHovered && !this.state.isDragging) {
      this.setState({ isDragging: true });
    }
  }

  /**
  *  @param {boolean} renameEditMode
  *  sets dragging state
  */
  _renameEditMode(renameEditMode) {
    this.setState({ renameEditMode });
  }

  /**
  *  @param {Object} evt
  *  sets dragging state
  */
  _updateFileName(evt) {
    this.setState({
      newFileName: evt.target.value,
    });
  }
  /**
  *  @param {Object} evt
  *  sets dragging state
  *  @return {}
  */
  _submitRename(evt) {
    if (evt.key === 'Enter') {
      this._triggerMutation();
    }

    if (evt.key === 'Escape') {
      this._clearState();
    }
  }

  /**
  *  @param {}
  *  sets state on a boolean value
  *  @return {}
  */
  _clearState() {
    this.setState({
      newFileName: this.props.filename,
      renameEditMode: false,
    });
  }

  /**
  *  @param {}
  *  triggers move mutation and clearState function
  *  @return {}
  */
  _triggerMutation() {
    let fileKeyArray = this.props.fileData.edge.node.key.split('/');
    fileKeyArray.pop();
    let folderKeyArray = fileKeyArray;
    let folderKey = folderKeyArray.join('/');
    let newKey = (folderKey.length > 0) ? `${folderKey}/${this.state.newFileName}` : this.state.newFileName;

    this._clearState();
    if (this.props.fileData.edge.node.key !== newKey) {
      const data = {
        newKey: `${folderKey}/${this.state.newFileName}`,
        edge: this.props.fileData.edge,
        removeIds: [this.props.fileData.edge.node.id],
      };

      this.props.mutations.moveLabbookFile(data, (response) => {
      });
    }
  }

  /**
  *  @param {object} event
  *  @param {boolean} hover - hover state for mouseover
  *  sets hover state
  *  @return {}
  */
  _setHoverState(evt, hover) {
    evt.preventDefault();

    if (this.state.hover !== hover) {
      this.setState({ hover });
    }

    if (this.props.setParentHoverState && hover) {
      this.props.setParentHoverState(evt, !hover);
    }
  }

  render() {
    const { node } = this.props.fileData.edge;
    const { index } = this.props.fileData;
    const fileName = this.props.filename;
    const fileRowCSS = classNames({
            File__row: true,
            'File__row--hover': this.state.hover,
            'File__row--background': this.props.isDragging,
          }),
          buttonCSS = classNames({
            'Btn Btn--round': true,
            'Btn--uncheck': !this.state.isSelected,
            'Btn--check': this.state.isSelected,
          }),
          textIconsCSS = classNames({
            'File__cell File__cell--name': true,
            hidden: this.state.renameEditMode,
          }),
          renameCSS = classNames({
            'File__cell File__cell--edit': true,
            hidden: !this.state.renameEditMode,
          }),
          paddingLeft = 40 * index,
          rowStyle = { paddingLeft: `${paddingLeft}px` };

    let file = <div
      style={this.props.style}
      onMouseOver={(evt) => { this._setHoverState(evt, true); }}
      onMouseOut={(evt) => { this._setHoverState(evt, false); }}
      onMouseLeave={() => { this._mouseLeave(); }}
      onMouseEnter={() => { this._mouseEnter(); }}
      className="File">

             <div
               className={fileRowCSS}
               style={rowStyle}
               >

                <button
                    className={buttonCSS}
                    onClick={() => { this._setSelected(!this.state.isSelected); }}>
                </button>

                <div className={textIconsCSS}>

                  <div className={`File__icon ${fileIconsJs.getClass(fileName)}`}></div>

                  <div className="File__text">
                  {
                    this.props.expanded &&
                    <TextTruncate
                      className="File__paragragh"
                      line={1}
                      truncateText="…"
                      text={fileName}
                    />
                  }
                  </div>

                </div>

                <div className={renameCSS}>

                  <div className="File__container">
                    <input
                      draggable
                      ref={(input) => { this.reanmeInput = input; }}
                      value={this.state.newFileName}
                      type="text"
                      className="File__input"
                      onClick={(evt) => { evt.preventDefault(); evt.stopPropagation(); }}
                      onDragStart={(evt) => { evt.preventDefault(); evt.stopPropagation(); }}
                      onChange={(evt) => { this._updateFileName(evt); }}
                      onKeyDown={(evt) => { this._submitRename(evt); }}
                    />
                  </div>
                  <div className="flex justify-space-around">
                    <button
                      className="File__btn--round File__btn--cancel"
                      onClick={() => { this._clearState(); }} />
                    <button
                      className="File__btn--round File__btn--add"
                      onClick={() => { this._triggerMutation(); }}
                    />
                  </div>
                </div>

                <div className="File__cell File__cell--size">
                    {config.humanFileSize(node.size)}
                </div>

                <div className="File__cell File__cell--date">
                    {Moment((node.modifiedAt * 1000), 'x').fromNow()}
                </div>

                <div className="File__cell File__cell--menu">
                  {
                    this.props.section === 'data' ?
                      <DatasetActionsMenu
                      edge={this.props.fileData.edge}
                      section={this.props.section}
                      mutationData={this.props.mutationData}
                      mutations={this.props.mutations}
                      renameEditMode={ this._renameEditMode }
                    />
                     :
                     <ActionsMenu
                     edge={this.props.fileData.edge}
                     mutationData={this.props.mutationData}
                     mutations={this.props.mutations}
                     renameEditMode={ this._renameEditMode }
                   />
                  }
                </div>

            </div>
        </div>;

    return (
      this.props.connectDragSource(file)
    );
  }
}

const FolderDND = DragSource(
  'card',
  Connectors.dragSource,
  Connectors.dragCollect,
)((File));


export default FolderDND;
