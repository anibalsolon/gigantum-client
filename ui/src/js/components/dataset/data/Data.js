// vendor
import React, { Component } from 'react';
import { createFragmentContainer, graphql } from 'react-relay';
// components
import DataBrowser from './DataBrowser';
// import DataFavorites from './DataFavorites';
// import MostRecent from 'Components/datasets/filesShared/MostRecentData';
import ToolTip from 'Components/shared/ToolTip';

class Data extends Component {
  constructor(props) {
  	super(props);
    this.state = {
      selectedFiles: [],
      // selectedFilter: 'favorites',
    };
    this._setSelectedFiles = this._setSelectedFiles.bind(this);
    this._clearSelectedFiles = this._clearSelectedFiles.bind(this);
    this._loadStatus = this._loadStatus.bind(this);
    this._selectFilter = this._selectFilter.bind(this);
  }
  componentDidUpdate() {
    // this.refs[this.state.selectedFilter].classList.add('Data__filter--selected');
    // for (const key in this.refs) {
    //   if (key !== this.state.selectedFilter) {
    //     this.refs[key].classList.remove('Data__filter--selected');
    //   }
    // }
  }

  _setSelectedFiles(evt) {
    const files = [...evt.target.files];
    this.setState({ selectedFiles: files });
  }

  _clearSelectedFiles() {
    this.setState({ selectedFiles: [] });
  }

  _loadStatus(res) {
    if (res !== this.state.loadingStatus) {
      this.setState({ loadingStatus: res });
    }
  }
  _selectFilter(filterName) {
    this.setState({ selectedFilter: filterName });
  }

  render() {
    if (this.props.datasets) {
      return (

        <div className="Data">
          <div className="Data__header">
            <div className="Data__subtitle-container">
              <h5 className="Data__subtitle">Data Browser
                <ToolTip section="dataBrowser" />
                {
                  this.state.loadingStatus &&
                  <div className="Data__loading" />
                }
              </h5>
              <p className="Data__subtitle-sub">Currently only files under 1.8GB are supported.</p>
            </div>

            <div className="Data__toolbar end">
              <p className="Data__import-text" id="Data__">
                <label
                  className="Data__import-file"
                  htmlFor="file__data"
                >
                  Upload File
                </label>
                <input
                  id="file__data"
                  className="hidden"
                  type="file"
                  onChange={(evt) => { this._setSelectedFiles(evt); }}
                />
                or Drag and Drop File Below
              </p>
            </div>
          </div>

          <div className="Data__file-browser">
            <DataBrowser
              selectedFiles={this.state.selectedFiles}
              clearSelectedFiles={this._clearSelectedFiles}
              datasetsId={this.props.datasetsId}
              dataId={this.props.datasets.id}
              data={this.props.datasets}
              loadStatus={this._loadStatus}
              type={this.props.type}
            />
          </div>
        </div>
      );
    }
    return (<div>No Files Found</div>);
  }
}


export default createFragmentContainer(
  Data,
  graphql`
    fragment Data_datasets on Dataset{
      id
      ...DataBrowser_data
    }
  `,
);
