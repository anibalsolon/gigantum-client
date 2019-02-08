// vendor
import React, { Component, Fragment } from 'react';
import classNames from 'classnames';
import { Link } from 'react-router-dom';
// config
import Config from 'JS/config';
// store
import store from 'JS/redux/store';
// components
import ToolTip from 'Components/common/ToolTip';
// assets
import './Navigation.scss';

export default class Navigation extends Component {

  render() {
    const { props } = this;
    const labbookLockCSS = classNames({
      [`Header__${visibility}`]: true,
      [`Header__${visibility}--sticky`]: props.isSticky,
    });

    return (
      <div className="Header__navContainer flex-0-0-auto">

      <ul className="Header__nav flex flex--row">
        {
          Config[`${this.props.sectionType}_navigation_items`].map((item, index) => (
            <NavItem
              self={this}
              item={item}
              index={index}
              key={item.id}
              type={this.props.sectionType}
            />))
        }

        <hr className={`Header__navSlider Header__navSlider--${selectedIndex}`} />
      </ul>

    </div>
    );
  }
}

/**
    @param {object, int}
    retruns jsx for nav items and sets selected
    @return {jsx}
*/
const NavItem = ({
  self,
  item,
  index, type,
}) => {
  const pathArray = self.props.location.pathname.split('/');
  const selectedPath = (pathArray.length > 4) ? pathArray[pathArray.length - 1] : 'overview'; // sets avtive nav item to overview if there is no menu item in the url

  const navItemCSS = classNames({
    'Header__navItem--selected': selectedPath === item.id,
    [`Header__navItem Header__navItem--${item.id}`]: !selectedPath !== item.id,
    [`Header__navItem--${index}`]: true,
  });

  const section = type === 'labbook' ? 'projects' : 'datasets';
  const name = type === 'labbook' ? self.props.match.params.labbookName : self.props.match.params.datasetName;

  return (
    <li
      id={item.id}
      className={navItemCSS}
      onClick={() => self._setSelectedComponent(item.id)}
      title={Config.navTitles[item.id]}
    >

      <Link
        onClick={self._scrollToTop}
        to={`../../../${section}/${self.props.owner}/${name}/${item.id}`}
        replace
      >

        {item.name}

      </Link>

    </li>);
};
