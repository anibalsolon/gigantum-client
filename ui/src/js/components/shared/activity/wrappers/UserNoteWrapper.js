// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
// components
import ToolTip from 'Components/common/ToolTip';
import UserNote from '../UserNote';
// assets
import './UserNoteWrapper.scss';

export default class UserNoteWrapper extends Component {
  constructor(props) {
  	super(props);
    this.state = {
      userNoteVisible: false,
    };

    this._toggleUserNote = this._toggleUserNote.bind(this);
  }

  /**
  *   @param {boolean} value
  *   sets state to show hide usernote
  *   @return {}
  */
  _toggleUserNote(userNoteVisible) {
    this.setState({ userNoteVisible });
  }

  render() {
    const { props, state } = this,
          userActivityContainerCSS = classNames({
            UserNote__container: true,
            'UserNote__container--open': state.userNoteVisible,
            fullscreen: props.editorFullscreen,
          }),
          userNoteCardCSS = classNames({
            'UserNote__add UserNote__card column-1-span-10': true,
            hidden: !state.userNoteVisible,
          }),
          buttonCSS = classNames({
             UserNote__button: true,
             'UserNote__button--close': state.userNoteVisible,
          });
    return (
      <div className={userActivityContainerCSS}>
        <ToolTip section="userNote" />
        <div
          className={buttonCSS}
          onClick={() => this._toggleUserNote(!state.userNoteVisible)}>
          <div className="UserNote__add-icon"></div>
          <div className="UserNote__text">Add Note</div>
        </div>
        <div className={userNoteCardCSS}>
          { state.userNoteVisible
            && <UserNote
                toggleUserNote={this._toggleUserNote}
                key="UserNote"
                {...props}
              />
          }
        </div>
      </div>
    );
  }
}
