// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
import { WithContext as ReactTags } from 'react-tag-input';
// assets
import './AdvancedSearch.scss';

export default class Modal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      expandedIndex: null,
    };
    this._resetSelectedFilter = this._resetSelectedFilter.bind(this);
  }
  /**
     *  @param {}
     *  add event listeners
  */
  componentDidMount() {
    window.addEventListener('click', this._resetSelectedFilter);
  }
  /**
     *  @param {}
     *  cleanup event listeners
  */
  componentWillUnmount() {
    window.removeEventListener('click', this._resetSelectedFilter);
  }
  /**
   *  @param {event} evt
   *  resets expanded index state
   *
  */
  _resetSelectedFilter(evt) {
    if (evt.target.className.indexOf('AdvancedSearch__filter-section') === -1) {
      this.setState({ expandedIndex: null });
    }
  }
  /**
    @param {number} i
    removes tag from list
  */
  _handleDelete = (i) => {
    const { tags } = this.props;

    tags.splice(i, 1);

    this.props.setTags(tags);
  }
  /**
    @param {number} i
    add tag to list
  */
  _handleAddition = (tag) => {
    const { tags } = this.props;

    tags.push({
      id: tags.length + 1,
      text: tag,
    });

    this.props.setTags(tags);
  }
  /**
    @param {number} i
    drags tag to new position.
  */
  _handleDrag = (tag, currPos, newPos) => {
    const { tags } = this.props;

    // mutate array
    tags.splice(currPos, 1);
    tags.splice(newPos, 0, tag);

    // re-render
    this.props.setTags(tags);
  }

  render() {
    const { tags } = this.props;
    return (
      <div className="AdvancedSearch">
        <ReactTags
           id="TagsInput"
           tags={tags}
           inline
           placeholder="Search by keyword, tags or filters"
           handleDelete={(index) => { this._handleDelete(index); }}
           handleAddition={(tag) => { this._handleAddition(tag); }}
           handleDrag={(tag, currPos, newPos) => { this._handleDrag(tag, currPos, newPos); }}
         />
        <div className="AdvancedSearch__filters">
        {
          Object.keys(this.props.filterCategories).map((category, index) =>
          <div
            key={category}
            className="AdvancedSearch__filter-container"
          >
            <div
                className={`AdvancedSearch__filter-section ${this.state.expandedIndex === index ? 'selected' : ''}`}
                onClick={() => this.setState({ expandedIndex: this.state.expandedIndex === index ? null : index })}
                key={category}
            >
                {category}
            </div>
            {
                this.state.expandedIndex === index &&
                <ul
                    className="AdvancedSearch__filter-list"
                >
                    {
                        this.props.filterCategories[category].map(filter =>
                            <li
                                key={filter}
                                onClick={() => this._handleAddition(filter)}
                            >
                                {filter}
                            </li>)
                    }
                </ul>
            }
          </div>)
        }
        </div>
      </div>
    );
  }
}
