// mutations
import CreateExperimentalBranchMutation from 'Mutations/branches/CreateExperimentalBranchMutation';
import DeleteExperimentalBranchMutation from 'Mutations/branches/DeleteExperimentalBranchMutation';
import MergeFromBranchMutation from 'Mutations/branches/MergeFromBranchMutation';
import PublishDatasetMutation from 'Mutations/branches/PublishDatasetMutation';
import PublishLabbookMutation from 'Mutations/branches/PublishLabbookMutation';
import ResetBranchToRemoteMutation from 'Mutations/branches/ResetBranchToRemoteMutation';
import SyncDatasetMutation from 'Mutations/branches/SyncDatasetMutation';
import SyncLabbookMutation from 'Mutations/branches/SyncLabbookMutation';
import WorkonExperimentalBranchMutation from 'Mutations/branches/WorkonExperimentalBranchMutation';

// store
import store from 'JS/redux/store';
import { setErrorMessage } from 'JS/redux/reducers/footer';
import { setIsProcessing } from 'JS/redux/reducers/dataset/dataset';

class BranchesMutations {
   /**
    * @param {Object} props
    *        {string} props.owner
    *        {string} props.name
    *        {string} props.connection
    *        {string} props.parentId
    * pass above props to state
    */
   constructor(props) {
    this.state = props;
   }

   /**
   *  @param {Object} data
   *         {string} data.branchName
   *         {string} data.revision
   *         {string} data.description
   *  @param {function} callback
   *  creates a new branch and checks it out
   */
   createBranch(data, callback) {
     const {
       branchName,
       revision,
       description,
     } = data;

     const { owner, name } = this.state;

    CreateExperimentalBranchMutation(
      owner,
      name,
      branchName,
      revision,
      description,
      callback,
    );
   }


   /**
   *  @param {Object} data
   *         {string} data.branchName
   *         {string} data.labbookId
   *  @param {function} callback
   *  deletes a branch
   */
   deleteBranch(data, callback) {
     const {
       branchName,
       revision,
       description,
     } = data;

    const { owner, name } = this.state;

    CreateExperimentalBranchMutation(
      owner,
      labbookName,
      branchName,
      labbookId,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *         {string} data.otherBranchName
   *         {boolean} data.overrideMethod
   *  @param {function} callback
   *  merges an elected branch into current active branch
   */
   merge(data, callback) {
     const {
       otherBranchName,
       overrideMethod,
     } = data;

     const { owner, name } = this.state;

    CreateExperimentalBranchMutation(
      owner,
      name,
      otherBranchName,
      overrideMethod,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *         {string} data.setPublic
   *         {function} data.successCall
   *         {function} data.failureCall
   *  @param {function} callback
   *  publishes dataset to a repository
   */
   publishDataset(data, callback) {
     const {
       setPublic,
       successCall,
       failureCall,
     } = data;

    const { owner, name } = this.state;

    PublishDatasetMutation(
      owner,
      name,
      setPublic,
      successCall,
      failureCall,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *         {string} data.labbookId
   *         {string} data.setPublic
   *         {function} data.successCall
   *         {function} data.failureCall
   *  @param {function} callback
   *  publishes labbook (project) to a repository
   */
   publishLabbook(data, callback) {
     const {
       labbookId,
       setPublic,
       successCall,
       failureCall,
     } = data;

    const { owner, name } = this.state;

    PublishLabbookMutation(
      owner,
      name,
      labbookId,
      setPublic,
      successCall,
      failureCall,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *  @param {function} callback
   *  resets branch to remote HEAD
   */
   resetBranch(data, callback) {
    const { owner, name } = this.state;

    ResetBranchToRemoteMutation(
      owner,
      name,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *         {boolean} data.force
   *         {function} data.successCall
   *         {function} data.failureCall
   *  @param {function} callback
   *  pulls and pushes branch
   */
   syncDataset(data, callback) {
     const {
       force,
       successCall,
       failureCall,
     } = data;
    const { owner, name } = this.state;

    SyncDatasetMutation(
      owner,
      name,
      force,
      successCall,
      failureCall,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *         {boolean} data.overrideMethod
   *         {function} data.successCall
   *         {function} data.failureCall
   *  @param {function} callback
   *  pulls and pushes branch
   */
   syncLabbook(data, callback) {
     const {
       overrideMethod,
       successCall,
       failureCall,
     } = data;
    const { owner, name } = this.state;

    SyncLabbookMutation(
      owner,
      name,
      overrideMethod,
      successCall,
      failureCall,
      callback,
    );
   }

   /**
   *  @param {Object} data
   *         {string} data.branchName
   *  @param {function} callback
   *  checksout branch
   */
   switchBranch(data, callback) {
     const {
       branchName,
     } = data;
    const { owner, name } = this.state;

    WorkonExperimentalBranchMutation(
      owner,
      name,
      branchName,
      callback,
    );
   }
}

export default BranchesMutations;
