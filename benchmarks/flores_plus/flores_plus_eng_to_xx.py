from datasets import get_dataset_config_names, load_dataset
import csv
import os

class FloresDatasetProcessor:
    
    def __init__(self, dataset_name="openlanguagedata/flores_plus"):
        self.dataset_name = dataset_name
        self.available_configs = self._get_available_configs()
    
    def _get_available_configs(self):
        """Get all available language configurations from the dataset."""
        try:
            configs = get_dataset_config_names(self.dataset_name)
            if "default" in configs:
                configs.remove("default")
            return configs
        except Exception as e:
            print(f"Error getting configs: {e}")
            return []
    
    def get_available_subsets(self):
        """Get available subsets for this dataset, handling authentication gracefully."""
        try:
            subsets = [config for config in get_dataset_config_names(self.dataset_name)]
            if "default" in subsets:
                subsets.remove("default")
            return subsets
        except Exception as e:
            print(f"Could not get dataset configs (may require authentication): {e}")
            # Return common language codes as fallback
            return ["fra", "deu", "spa", "ita", "por", "rus", "zho", "jpn", "ara", "hin"]
    
    def extract_language_pairs_to_csv(self, target_language_code, output_file=None, split="dev"):
        """
        Extract English-target language pairs and save to CSV.
        
        Args:
            target_language_code (str): The target language code (e.g., 'fra', 'deu', 'spa')
            output_file (str, optional): Output CSV filename. If None, auto-generates name.
            split (str): Dataset split to use (default: 'dev')
        
        Returns:
            str: Path to the created CSV file
        """
        # Auto-generate filename if not provided
        if output_file is None:
            output_file = f"flores_eng_to_{target_language_code}.csv"
        
        # Validate target language config exists
        if target_language_code not in self.available_configs:
            raise ValueError(f"Target language '{target_language_code}' not found in available configs: {self.available_configs[:10]}...")
        
        try:
            # Load the dataset for the target language
            dataset = load_dataset(
                self.dataset_name,
                name=target_language_code,
                split=split
            )
            
            # Get first example to understand structure
            try:
                first_example = next(iter(dataset))
                columns = []
                if isinstance(first_example, dict):
                    columns = list(first_example.keys())
                print(f"Available columns in dataset: {columns}")
            except (StopIteration, AttributeError) as e:
                raise ValueError(f"Could not examine dataset structure: {e}")
            
            # Extract English-target language pairs
            pairs = []
            
            for idx, example in enumerate(dataset):
                try:
                    english_text = None
                    target_text = None
                    
                    # Try different possible field names for English
                    for eng_field in ['eng', 'english', 'en', 'eng_Latn']:
                        if eng_field in example:
                            english_text = example[eng_field]
                            break
                    
                    # Try different possible field names for target language
                    for target_field in [target_language_code, f'{target_language_code}_Latn', 'target', 'translation']:
                        if target_field in example:
                            target_text = example[target_field]
                            break
                    
                    # If we found both texts, add to pairs with metadata
                    if english_text is not None and target_text is not None:
                        # Create row with metadata
                        row_data = [
                            str(english_text),
                            str(target_text),
                            target_language_code,  # language code
                            idx,  # sentence id
                            len(str(english_text).split()),  # english word count
                            len(str(target_text).split())   # target word count
                        ]
                        pairs.append(row_data)
                    else:
                        # If standard field names don't work, try to use first two columns
                        if len(columns) >= 2:
                            first_col = columns[0]
                            second_col = columns[1]
                            if first_col in example and second_col in example:
                                english_text = example[first_col]  # Assume first column is English
                                target_text = example[second_col]   # Assume second column is target
                                row_data = [
                                    str(english_text),
                                    str(target_text),
                                    target_language_code,
                                    idx,
                                    len(str(english_text).split()),
                                    len(str(target_text).split())
                                ]
                                pairs.append(row_data)
                        
                        if len(pairs) <= idx:  # If we didn't add this row
                            print(f"Could not process row {idx}: available fields {list(example.keys())}")
                            if idx == 0:  # Stop if we can't process the first row
                                raise ValueError("Could not identify English and target language fields in first row")
                
                except Exception as row_error:
                    print(f"Error processing row {idx}: {row_error}")
                    if idx == 0:  # If first row fails, abort
                        raise
                    continue  # Skip this row and continue
            
            if not pairs:
                raise ValueError("No valid language pairs found in dataset")
            
            # Write to CSV with headers
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header with language name and metadata
                headers = [
                    'english', 
                    f'{target_language_code}_text', 
                    'language_code',
                    'sentence_id',
                    'english_word_count',
                    'target_word_count'
                ]
                writer.writerow(headers)
                # Write data
                writer.writerows(pairs)
            
            print(f"Successfully extracted {len(pairs)} language pairs to {output_file}")
            print(f"Columns: {headers}")
            return output_file
            
        except Exception as e:
            print(f"Error processing dataset: {e}")
            raise
    
    def list_available_languages(self):
        """List all available language configurations."""
        return self.available_configs 