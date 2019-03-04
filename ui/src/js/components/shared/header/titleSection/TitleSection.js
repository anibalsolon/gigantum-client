// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
// store
import store from 'JS/redux/store';
// mutations
import SetLabbookDescriptionMutation from 'Mutations/SetLabbookDescriptionMutation';
// components
import ToolTip from 'Components/common/ToolTip';
import Description from './description/Description';
// assets
import './TitleSection.scss';

export default class TitleSection extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const { props } = this,
          {
            sectionType,
          } = props,
          section = props[sectionType],
          {
            visibility,
          } = section,
          visibilityIconCSS = classNames({
            [`TitleSection__${visibility}`]: true,
            [`TitleSection__${visibility}--sticky`]: props.isSticky,
            'Tooltip-data Tooltip-data--small': true,
          }),
          title = `${section.owner} / ${section.name}`;
    return (
      <div className="TitleSection">

        <div className="TitleSection__namespace">
          <div className="TitleSection__namespace-title">{title}</div>
          { ((visibility === 'private') || (visibility === 'public'))
              && <div
                className={visibilityIconCSS}
                data-tooltip={visibility}
              />
          }
        </div>

        {
          !props.isSticky && <Description {...props} />
        }
      </div>
    );
  }
}
