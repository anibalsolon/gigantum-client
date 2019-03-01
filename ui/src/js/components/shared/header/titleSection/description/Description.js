// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
// components
import ToolTip from 'Components/common/ToolTip';
// mutations
import SetLabbookDescriptionMutation from 'Mutations/SetLabbookDescriptionMutation';
import SetDatasetDescriptionMutation from 'Mutations/SetDatasetDescriptionMutation';
// store
import store from 'JS/redux/store';
// assets
import './Description.scss';

export default class Description extends Component {
  constructor(props) {
    super(props);
    this.state = {
      editingDescription: false,
      descriptionText: this.props.description ? this.props.description.replace(/\n/g, ' ') : '',
      lastSavedDescription: this.props.description ? this.props.description.replace(/\n/g, ' ') : '',
      savingDescription: false,
      hovered: false,
      textareaWidth: '270px',
      textareaHeight: '66px',
    };
    this._handleClick = this._handleClick.bind(this);
    this._saveDescription = this._saveDescription.bind(this);
    this._cancelDescription = this._cancelDescription.bind(this);
  }
  /*
    adds event listeners
  */
  componentDidMount() {
    window.addEventListener('click', this._handleClick);
  }
  /*
    removes event listeners
  */
  componentWillUnmount() {
    window.removeEventListener('click', this._handleClick);
  }
  /**
    *  @param {event} evt
    handles click outside description
  */
  _handleClick(evt) {
    if (evt.target.className.indexOf('Description') === -1 && this.state.editingDescription) {
      this._cancelDescription();
    }
  }
  /**
   @param {String} owner
   @param {String} labbookName
   calls mutation to save labbook description
   */
  _saveLabbookDescription(owner, labbookName) {
    SetLabbookDescriptionMutation(
      owner,
      labbookName,
      this.state.descriptionText.replace(/\n/g, ' '),
      (res, error) => {
        if (error) {
          console.log(error);
          setErrorMessage('Description was not set: ', error);
        } else {
          this.setState({ editingDescription: false, savingDescription: false, lastSavedDescription: this.state.descriptionText.replace(/\n/g, ' ') });
        }
      },
    );
  }

  /**
   @param {String} owner
   @param {String} labbookName
   calls mutation to save dataset description
   */
  _saveDatasetDescription(owner, labbookName) {
    SetDatasetDescriptionMutation(
      owner,
      labbookName,
      this.state.descriptionText.replace(/\n/g, ' '),
      (res, error) => {
        if (error) {
          console.log(error);
          setErrorMessage('Description was not set: ', error);
        } else {
          this.setState({ editingDescription: false, savingDescription: false, lastSavedDescription: this.state.descriptionText.replace(/\n/g, ' ') });
        }
      },
    );
  }

  /**
    *  @param {}
    *  fires setlabbookdescription mutation
  */
  _saveDescription() {
    const { owner, labbookName } = store.getState().routes;
    this.setState({ savingDescription: true });
    if (this.props.sectionType === 'labbook') {
      this._saveLabbookDescription(owner, labbookName);
    } else {
      this._saveDatasetDescription(owner, labbookName);
    }
  }
  /**
    *  @param {}
    *  reverts description back to last save
  */
  _cancelDescription() {
    this.setState({ editingDescription: false, descriptionText: this.state.lastSavedDescription });
  }
  /**
    *  @param {}
    *  handles enabling description editing and sets textareaCSS
  */
  _editingDescription() {
    if (!this.state.editingDescription) {
      let element = document.getElementsByClassName('Description__container')[0];
      let width = element.offsetWidth - 30;
      let height = element.offsetHeight - 4;
      this.setState({ editingDescription: true, textareaWidth: `${width}px`, textareaHeight: `${height}px` });
    }
  }

  render() {
    const { props, state } = this,
          descriptionCSS = classNames({
            Description__text: true,
            empty: !this.state.descriptionText,
          }),
          descriptionContainerCSS = classNames({
              Description__container: true,
              'Description__container--hovered': this.state.hovered && !this.state.editingDescription,
              'visibility-hidden': this.props.hovered,
          }),
          displayedText = this.state.descriptionText && this.state.descriptionText.length ? this.state.descriptionText : 'Add description...',
          defaultText = this.state.descriptionText ? this.state.descriptionText : '';

    return (
     <div className="Description">

            <div className={descriptionContainerCSS}
                onMouseEnter={() => this.setState({ hovered: true })}
                onMouseLeave={() => this.setState({ hovered: false })}
                onClick={() => this._editingDescription()}>

            {
                this.state.editingDescription ?
                  <Fragment>
                    <textarea
                        maxLength="80"
                        className="Description__input"
                        type="text"
                        onChange={(evt) => { this.setState({ descriptionText: evt.target.value.replace(/\n/g, ' ') }); }}
                        onKeyDown={(evt) => {
                            if (evt.key === 'Enter') {
                                this.setState({ editingDescription: false });
                                this._saveDescription();
                            }
                        }}
                        placeholder="Short description of Project"
                        defaultValue={defaultText}
                    />
                    <div
                      className="Description__input-buttons"
                      style={{ height: state.textareaHeight }}>
                        <button
                          onClick={this._cancelDescription}
                          className="Description__input-cancel"
                        />
                        <button
                          onClick={this._saveDescription}
                          className="Description__input-save"
                        />
                    </div>
                  </Fragment>
                :
                    <p className={descriptionCSS}>
                        {displayedText}
                        { state.hovered
                          && <button className="Description__edit-button" />
                        }
                    </p>
            }
            </div>
        <ToolTip section="descriptionOverview" />
     </div>
    );
  }
}
