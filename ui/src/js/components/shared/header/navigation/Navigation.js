// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
import { Link } from 'react-router-dom';
import { boundMethod } from 'autobind-decorator';
// config
import Config from 'JS/config';
// store
import store from 'JS/redux/store';
import {
  setSyncingState,
  setPublishingState,
  setExportingState,
  setModalVisible,
  setUpdateDetailView,
} from 'JS/redux/reducers/labbook/labbook';
// components
import ToolTip from 'Components/common/ToolTip';
// assets
import './Navigation.scss';

class Navigation extends Component {
  /**
    @param {string} componentName - input string componenetName
    updates state of selectedComponent
    updates history prop
  */
  @boundMethod
  _setSelectedComponent(componentName) {
    if (componentName !== this.props.selectedComponent) {
      if (store.getState().detailView.selectedComponent === true) {
        setUpdateDetailView(false);
      }
    }
  }

  /**
    @param {object} item
    @returns {Number} selectedIndex
  */
  @boundMethod
  _getSelectedIndex() {
    const { props } = this,
          pathArray = this.props.location.pathname.split('/'),
          defaultOrder = Config[`${this.props.sectionType}DefaultNavOrder`],
          selectedPath = (pathArray.length > 4) ? pathArray[pathArray.length - 1] : defaultOrder[0],
          selectedIndex = defaultOrder.indexOf(selectedPath);
    return selectedIndex;
  }

  render() {
    const { props, state } = this,
          { visibility } = props[props.sectionType],
          selectedIndex = this._getSelectedIndex(),
          labbookLockCSS = classNames({
            [`Header__${visibility}`]: true,
            [`Header__${visibility}--sticky`]: props.isSticky,
          }),
          section = (props.sectionType === 'labbook') ? 'projects' : 'datasets',
          name = (props.sectionType === 'labbook') ? props.match.params.labbookName : props.match.params.datasetName;

    return (
      <div className="Navigation flex-0-0-auto">

      <ul className="Navigation__ul flex flex--row">
        {
          Config[`${this.props.sectionType}_navigation_items`].map((item, index) => {
            const pathArray = props.location.pathname.split('/'),
                  selectedPath = (pathArray.length > 4) ? pathArray[pathArray.length - 1] : 'overview', // sets avtive nav item to overview if there is no menu item in the url
                  navItemCSS = classNames({
                    'Navigation__list-item--selected': (selectedPath === item.id),
                    [`Navigation__list-item Navigation__list-item--${item.id}`]: (!selectedPath !== item.id),
                    [`Navigation__list-item--${index}`]: true,
                  });

            return (
              <li
                id={item.id}
                key={item.id}
                className={navItemCSS}
                onClick={() => this._setSelectedComponent(item.id)}
                title={Config.navTitles[item.id]}>

                <Link
                  onClick={this._scrollToTop}
                  to={`../../../${section}/${props.owner}/${name}/${item.id}`}
                  replace>
                  {item.name}
                </Link>

              </li>);
          })
        }

        <hr className={`Navigation__slider Navigation__slider--${selectedIndex}`} />
      </ul>

    </div>
    );
  }
}

export default Navigation;
