import React from 'react';
import { DragSource } from 'react-dnd';
import uuidv4 from 'uuid/v4';
import FileBrowserMutations from './FileBrowserMutations';
// utilities
import CreateFiles from './../utilities/CreateFiles';
// store
import store from 'JS/redux/store';
// config
import config from 'JS/config';


/**
* @param {array} files
*
* @return {number} totalFiles
*/
const checkFileSize = (files, prompt) => {
  const tenMB = 10 * 1000 * 1000;
  const oneHundredMB = 100 * 1000 * 1000;
  const eighteenHundredMB = oneHundredMB * 18;
  const fileSizePrompt = [];
  const fileSizeNotAllowed = [];

  function filesRecursionCount(file) {
    if (Array.isArray(file)) {
      file.forEach((nestedFile) => {
        filesRecursionCount(nestedFile);
      });
    } else if (file.file && Array.isArray(file.file) && (file.file.length > 0)) {
      file.file.forEach((nestedFile) => {
        filesRecursionCount(nestedFile);
      });
    } else {
      const extension = file.name ? file.name.replace(/.*\./, '') : file.entry.fullPath.replace(/.*\./, '');

      if ((config.fileBrowser.excludedFiles.indexOf(extension) < 0) && ((file.entry && file.entry.isFile) || (typeof file.type === 'string'))) {
        if (prompt) {
          if (file.size > oneHundredMB) {
            fileSizeNotAllowed.push(file);
          }

          if ((file.size > tenMB) && (file.size < oneHundredMB)) {
            fileSizePrompt.push(file);
          }
        } else if (file.size > eighteenHundredMB) {
          fileSizeNotAllowed.push(file);
        }
      }
    }
  }
  filesRecursionCount(files);

  return { fileSizeNotAllowed, fileSizePrompt };
};

const dragSource = {

 canDrag(props) {
   // You can disallow drag based on props
   return true;
 },

 isDragging(props, monitor) {
    return monitor.getItem().key === props.key;
 },

 beginDrag(props, monitor) {
  return {
    isDragging: true,
    data: props.data,
  };
 },

  endDrag(props, monitor, component) {
    if (!monitor.didDrop()) {
      return;
    }

    const item = monitor.getItem();
    const dropResult = monitor.getDropResult();

    let fileNameParts = props.data.edge.node.key.split('/');

    let fileName = fileNameParts[fileNameParts.length - 1];
    if (dropResult.data) {
      let pathArray = dropResult.data.edge.node.key.split('/');
      pathArray.pop();
      let path = pathArray.join('/');

      let newKey = path ? `${path}/${fileName}` : `${fileName}`;

      let newKeyArray = dropResult.data.edge.node.key.split('/');
      let fileKeyArray = props.data.edge.node.key.split('/');

      newKeyArray.pop();
      fileKeyArray.pop();

      let newKeyPath = newKeyArray.join('/');
      let fileKeyPath = fileKeyArray.join('/');
      newKeyPath = newKeyPath.replace(/\/\/\/g/, '/');
      const trimmedFilePath = (fileKeyPath + (fileName.length ? `/${fileName}` : '')).split('/').slice(0, -1).join('/');

      if ((newKeyPath !== fileKeyPath) && (trimmedFilePath !== newKeyPath)) {
        if (newKey !== props.data.edge.node.key) {
          let removeIds = [props.data.edge.node.id];
          let currentHead = props.data;

          const searchChildren = (parent) => {
            if (parent.children) {
              Object.keys(parent.children).forEach((childKey) => {
                if (parent.children[childKey].edge) {
                  removeIds.push(parent.children[childKey].edge.node.id);
                  searchChildren(parent.children[childKey]);
                }
              });
            }
          };

          searchChildren(currentHead);

          const moveLabbookFileData = {
            newKey,
            edge: props.data.edge,
            removeIds,
          };

          if (props.mutations) {
            props.mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
          } else {
            const {
              parentId,
              connection,
              favoriteConnection,
              section,
            } = props;
            const { owner, labbookName } = store.getState().routes;

            const mutationData = {
              owner,
              labbookName,
              parentId,
              connection,
              favoriteConnection,
              section,
            };

            const mutations = new FileBrowserMutations(mutationData);

            mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
          }
        }
      }
    }
  },
};

function dragCollect(connect, monitor) {
  return {
    connectDragPreview: connect.dragPreview(),
    connectDragSource: connect.dragSource(),
    isDragging: monitor.sourceId === monitor.getSourceId(),
  };
}

const uploadDirContent = (dndItem, props, mutationData, fileSizeData) => {
  let path;
  dndItem.dirContent.then((fileList) => {
      if (fileList.length) {
        let key = props.data ? props.data.edge.node.key : props.fileKey ? props.fileKey : '';
        path = key === '' ? '' : key.substr(0, key.lastIndexOf('/') || key.length);

        CreateFiles.createFiles(fileList.flat(), `${path}/`, mutationData, props, fileSizeData);
      } else if (dndItem.files && dndItem.files.length) {
           // handle dragged files
           let key = props.newKey || props.fileKey;
           path = key.substr(0, key.lastIndexOf('/') || key.length);
           let item = monitor.getItem();

           if (item && item.files && props.browserProps.createFiles) {
             CreateFiles.createFiles(item.files, `${path}/`, mutationData, props, fileSizeData);
           }
           newPath = null;
           fileKey = null;
      }
  });
};

const targetSource = {
  canDrop(props, monitor) {
     const { uploading } = store.getState().fileBrowser;
     return monitor.isOver({ shallow: true }) && !uploading;
  },
  drop(props, monitor, component) {
    const dndItem = monitor.getItem();
    const prompt = (props.section === 'code') || (props.mutationData && (props.mutationData.section === 'code'));

    let newPath,
        fileKey,
        path,
        files;
    if (dndItem && props.data) {
          if (!dndItem.dirContent) {
              fileKey = props.data.edge.node.key;

              const fileNameParts = fileKey.split('/');
              const fileName = fileNameParts[fileNameParts.length - 1];
              let newKey = props.newKey || props.fileKey;
              newPath = newKey + fileName;
              fileKey = props.fileKey;
          } else {
            let fileSizeData = checkFileSize(dndItem.files, prompt);
            if (fileSizeData.fileSizePrompt.length === 0) {
               uploadDirContent(dndItem, props, props.mutationData, fileSizeData);
            } else {
               props.codeDirUpload(dndItem, props, props.mutationData, uploadDirContent, fileSizeData);
            }
          }
      } else {
          const {
            parentId,
            connection,
            favoriteConnection,
            section,
          } = props;
          const { owner, labbookName } = store.getState().routes;

          const mutationData = {
            owner,
            labbookName,
            parentId,
            connection,
            favoriteConnection,
            section,
          };
          // uploads to root directory
          let item = monitor.getItem();
          if (item.files) {
            let fileSizeData = checkFileSize(item.files, prompt);
            if (fileSizeData.fileSizePrompt.length === 0) {
              if (dndItem.dirContent) {
                 uploadDirContent(dndItem, props, mutationData, fileSizeData);
              } else {
                 CreateFiles.createFiles(item.files, '', component.state.mutationData, props, fileSizeData);
              }
            } else if (dndItem.dirContent) {
                component._codeDirUpload(dndItem, props, mutationData, uploadDirContent, fileSizeData);
            } else {
                component._codeFileUpload(item.files, props, component.state.mutationData, CreateFiles.createFiles, fileSizeData);
            }
          } else {
            const dropResult = monitor.getDropResult();
            let currentKey = item.data.edge.node.key;
            let splitKey = currentKey.split('/');
            let newKeyTemp = (splitKey[splitKey.length - 1] !== '') ? splitKey[splitKey.length - 1] : splitKey[splitKey.length - 2];
            let splitFolder = dropResult && dropResult.data ? dropResult.data.edge.node.key.split('/') : [''];
            if (splitFolder !== '') {
              splitFolder.pop();
            }

            let dropFolderKey = splitFolder.join('/');

            let newKey = item.data && item.data.edge.node.isDir ? `${dropFolderKey}/${newKeyTemp}/` : `${dropFolderKey}/${newKeyTemp}`;
            newKey = dropResult && dropResult.data ? newKey : `${newKeyTemp}`;

            if ((newKey !== item.data.edge.node.key) && ((`${newKey}/`) !== item.data.edge.node.key)) {

              let removeIds = [item.data.edge.node.id];
              let currentHead = item.data;

              const searchChildren = (parent) => {
                if (parent.children) {
                  Object.keys(parent.children).forEach((childKey) => {
                    if (parent.children[childKey].edge) {
                      removeIds.push(parent.children[childKey].edge.node.id);
                      searchChildren(parent.children[childKey]);
                    }
                  });
                }
              };

              searchChildren(currentHead);

              const moveLabbookFileData = {
                newKey,
                edge: item.data.edge,
                removeIds,
              };

              if (props.mutations) {
                props.mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
              } else {
                const {
                  parentId,
                  connection,
                  favoriteConnection,
                  section,
                } = props;
                const { owner, labbookName } = store.getState().routes;

                const mutationData = {
                  owner,
                  labbookName,
                  parentId,
                  connection,
                  favoriteConnection,
                  section,
                };

                const mutations = new FileBrowserMutations(mutationData);

                mutations.moveLabbookFile(moveLabbookFileData, (response) => {});
              }
            }
          }
      }

      return {
       data: props.data,
      };
  },
};

function targetCollect(connect, monitor) {
  let currentTargetId = monitor.targetId;
  let isOverCurrent = monitor.isOver({ shallow: true });
  let isOver = monitor.isOver({});
  let canDrop = monitor.canDrop();
  let currentTarget = monitor.internalMonitor.registry.dropTargets.get(currentTargetId);

  let newLastTarget;

  let targetIds = monitor.internalMonitor.getTargetIds();
  let targets = targetIds.map(id => monitor.internalMonitor.registry.dropTargets.get(id));
  if (targets.length > 0) {
    let lastTarget = targets[targets.length - 1];
    if (lastTarget.props.data && !lastTarget.props.data.edge.node.isDir) {
      targets.pop();
    }
    newLastTarget = targets[targets.length - 1];
    isOver = (currentTargetId === newLastTarget.monitor.targetId);
  } else {
    isOver = false;
  }

  let dragItem;
  monitor.internalMonitor.registry.dragSources.forEach((item) => {
    if (item.ref && item.ref.current && item.ref.current.props.isDragging) {
      dragItem = item.ref.current;
    }
  });

  if (dragItem && newLastTarget) {
    let dragKeyArray = dragItem.props.data.edge.node.key.split('/');
    dragKeyArray.pop();

    let dragKeyPruned = dragKeyArray.join('/') === '' ? '' : `${dragKeyArray.join('/')}/`;

    let dropKey = newLastTarget.props.files ? '' : newLastTarget.props.data.edge.node.key;
    canDrop = (dragKeyPruned !== dropKey);
    isOver = isOver && canDrop;
  }
  const { uploading } = store.getState().fileBrowser;
  isOver = isOver && !uploading;

  return {
    connectDropTarget: connect.dropTarget(),
		canDrop,
    isOver,
    isOverCurrent,
  };
}

const Connectors = {
  dragSource,
  dragCollect,
  targetSource,
  targetCollect,
};

export default Connectors;
