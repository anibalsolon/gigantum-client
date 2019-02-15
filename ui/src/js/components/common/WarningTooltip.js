import React, { Component } from 'react';
import classNames from 'classnames';
import { connect } from 'react-redux';
// store
import store from 'JS/redux/store';
// config
import config from 'JS/config';
// assets
import './WarningTooltip.scss';

const getPoints = (position) => {
  let pointerPoints = {};
  let messagePoints = {};

  if (position.points === undefined) {
    pointerPoints = {
      bottom: '-1px',
      left: 'calc(50% - 175px)',
    };
    pointerPoints = {
      bottom: '-7px',
      left: 'calc(50% - 175px)',
    };
  } else if (position.type === 'left') {
    pointerPoints = {
      top: `${position.points.top}px`,
      right: `${position.points.right}px`,
    };

    let messageRight = position.points.right + 8;
    messagePoints = {
      top: `${position.points.top}px`,
      right: `${messageRight}px`,
    };
  } else if (position.type === 'right') {
    pointerPoints = {
      top: `${position.points.top}px`,
      left: `${position.points.left}px`,
    };

    let messageRight = position.points.left + 6;
    let messageTop = position.points.top - 8;
    messagePoints = {
      top: `${messageTop}px`,
      left: `${messageRight}px`,
    };
  } else if (position.type === 'top') {
    pointerPoints = {};
    messagePoints = {};
  } else if (position.type === 'down') {
    pointerPoints = {};
    messagePoints = {};
  }

  return ({ pointerPoints, messagePoints });
};

class WarningToolTip extends Component {

  render() {
    const { props } = this,
          positionClass = `Tooltip__position--${props.position.type}`,
          toolTipCSS = classNames({
            ToolTip: props.isVisible,
            [positionClass]: true,
            hidden: !props.isVisible,
          }),
          { pointerPoints, messagePoints } = getPoints(props.position);

    return (
      <div className={toolTipCSS}>
        <div
          style={pointerPoints}
          className="WarningoolTip__pointer" />
        <div
          style={messagePoints}
          className="WarningToolTip__message">
          {props.message}
        </div>

      </div>
    );
  }
}

export default WarningToolTip;
